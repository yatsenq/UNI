using System;
using System.Diagnostics;
using System.Threading;
using System.Collections.Generic;

class PrimParallel
{
    static int n;
    static int maxThreads;
    static int[,] graph;
    static int source;
    static int[] parent;
    static Barrier barrier;
    static object lockObj = new object();
    const int INF = int.MaxValue / 2;

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        bool continueProgram = true;
        while (continueProgram)
        {
            Console.Clear();
            Console.Write("Введіть розмір графа (кількість вершин n): ");
            n = int.Parse(Console.ReadLine());
            Console.Write("Введіть максимальну кількість потоків (k): ");
            maxThreads = int.Parse(Console.ReadLine());

            Console.Write("Введіть стартову вершину a (0 до {0}): ", n - 1);
            source = int.Parse(Console.ReadLine());

            if (source < 0 || source >= n)
            {
                Console.WriteLine("\nПомилка: вершина повинна бути від 0 до {0}", n - 1);
                Console.WriteLine("Натисніть будь-яку клавішу для продовження...");
                Console.ReadKey();
                continue;
            }
            Console.WriteLine("\nГенерація графа та обчислення...\n");
            graph = GenerateRandomGraph(n);
            
            long sequentialTime = 0;
            long bestTime = long.MaxValue;
            int bestThreadCount = 1;
            double bestSpeedup = 1.0;
            double bestEfficiency = 100.0;
            int[] bestMSTParent = new int[n];
            int bestMSTWeight = 0;

            Console.WriteLine("=============================================================================");
            Console.WriteLine("|  Потоки    |  Час виконання (мс)   |   Прискорення   |   Ефективність (%)   |");
            Console.WriteLine("=============================================================================");

            for (int threads = 1; threads <= maxThreads; threads++)
            {
                int[] resultKey = new int[n];
                parent = new int[n];
                
                long executionTime;
                
                if (threads == 1)
                {
                    barrier = null;
                    executionTime = MeasureTime(() => PrimSequential(resultKey));
                    sequentialTime = executionTime;
                    Array.Copy(parent, bestMSTParent, n);
                    bestMSTWeight = CalculateMSTWeight();
                    
                    double speedup = 1.0;
                    double efficiency = 100.0;
                    
                    Console.WriteLine("| {0,10} | {1,21} | {2,15:F4} | {3,19:F2}% |",
                        threads, executionTime, speedup, efficiency);
                }
                else
                {
                    barrier = new Barrier(threads);
                    executionTime = MeasureTime(() => PrimParallelMethod(resultKey, threads));
                    
                    double speedup = (double)sequentialTime / executionTime;
                    double efficiency = (speedup / threads) * 100.0;

                    if (executionTime < bestTime)
                    {
                        bestTime = executionTime;
                        bestThreadCount = threads;
                        bestSpeedup = speedup;
                        bestEfficiency = efficiency;
                    }

                    Console.WriteLine("| {0,10} | {1,21} | {2,15:F4} | {3,19:F2}% |",
                        threads, executionTime, speedup, efficiency);
                }
            }

            Console.WriteLine("=============================================================================");
            
            int displayCount = Math.Min(10, n - 1);
            int edgeCount = 0;
            
            for (int i = 0; i < n && edgeCount < displayCount; i++)
            {
                if (bestMSTParent[i] != -1)
                {
                    Console.WriteLine("  a{0} ---- a{1}  (вага: {2})", 
                        bestMSTParent[i], i, graph[bestMSTParent[i], i]);
                    edgeCount++;
                }
            }
            
            if (n - 1 > displayCount)
                Console.WriteLine("  ... та ще {0} ребер", n - 1 - displayCount);
            Console.WriteLine();
            Console.WriteLine("===     Аналіз продуктивності     ===");
            Console.WriteLine();
            Console.WriteLine("1. Параметри графа:");
            Console.WriteLine("    1.1 Розмір: {0} × {0} вершин", n);
            Console.WriteLine("    1.2 Стартова вершина: a{0}", source);
            Console.WriteLine();
            Console.WriteLine("2. Час виконання:");
            Console.WriteLine("    2.1 Без потоків (послідовно, 1 потік): {0} мс", sequentialTime);
            Console.WriteLine("    2.2 З {0} потоками: {1} мс", bestThreadCount, bestTime);
            Console.WriteLine();
            Console.WriteLine("3.  Найкращий результат:");
            Console.WriteLine("    3.1 Оптимальна кількість потоків: {0}", bestThreadCount);
            Console.WriteLine("    3.2 Прискорення: {0:F4}x", bestSpeedup);
            Console.WriteLine("    3.3 Ефективність: {0:F2}%", bestEfficiency);

            Console.WriteLine("\n" + new string('─', 75));
            Console.Write("Бажаєте виконати ще один тест? (Y/N): ");
            string response = Console.ReadLine().Trim().ToUpper();
            continueProgram = (response == "Y" || response == "Т" || response == "YES" || response == "ТАК");
        }
    }

    static void PrimSequential(int[] key)
    {
        for (int i = 0; i < n; i++)
        {
            key[i] = INF;
            parent[i] = -1;
        }
        key[source] = 0;
        bool[] inMST = new bool[n];

        for (int count = 0; count < n; count++)
        {
            int u = MinKey(key, inMST);
            if (u == -1) break;
            inMST[u] = true;
            for (int v = 0; v < n; v++)
            {
                if (!inMST[v] && graph[u, v] != INF && graph[u, v] < key[v])
                {
                    key[v] = graph[u, v];
                    parent[v] = u;
                }
            }
        }
    }
    static void PrimParallelMethod(int[] key, int numThreads)
    {
        // Ініціалізація
        for (int i = 0; i < n; i++)
        {
            key[i] = INF;
            parent[i] = -1;
        }
        key[source] = 0;
        bool[] inMST = new bool[n];
        int[] localMin = new int[numThreads];
        int[] localMinIndex = new int[numThreads];

        Thread[] threads = new Thread[numThreads];
        int rowsPerThread = n / numThreads;

        for (int t = 0; t < numThreads; t++)
        {
            int threadId = t;
            int start = threadId * rowsPerThread;
            int end = (threadId == numThreads - 1) ? n : start + rowsPerThread;

            threads[threadId] = new Thread(() =>
            {
                for (int step = 0; step < n; step++)
                {
                    localMin[threadId] = INF;
                    localMinIndex[threadId] = -1;
                    
                    for (int v = start; v < end; v++)
                    {
                        if (!inMST[v] && key[v] < localMin[threadId])
                        {
                            localMin[threadId] = key[v];
                            localMinIndex[threadId] = v;
                        }
                    }
                    barrier.SignalAndWait();
                    int u = -1;
                    if (threadId == 0)
                    {
                        int globalMin = INF;
                        for (int i = 0; i < numThreads; i++)
                        {
                            if (localMin[i] < globalMin)
                            {
                                globalMin = localMin[i];
                                u = localMinIndex[i];
                            }
                        }
                        
                        if (u != -1)
                        {
                            inMST[u] = true;
                        }
                        localMinIndex[0] = u; 
                    }
                    barrier.SignalAndWait();
                    
                    u = localMinIndex[0];
                    if (u == -1) continue;

                    for (int v = start; v < end; v++)
                    {
                        if (!inMST[v] && graph[u, v] != INF && graph[u, v] < key[v])
                        {
                            lock (lockObj)
                            {
                                if (graph[u, v] < key[v])
                                {
                                    key[v] = graph[u, v];
                                    parent[v] = u;
                                }
                            }
                        }
                    }
                    barrier.SignalAndWait();
                }
            });
            threads[threadId].Start();
        }
        foreach (Thread t in threads)
            t.Join();
    }
    static int MinKey(int[] key, bool[] inMST)
    {
        int min = INF, minIndex = -1;
        for (int v = 0; v < n; v++)
        {
            if (!inMST[v] && key[v] < min)
            {
                min = key[v];
                minIndex = v;
            }
        }
        return minIndex;
    }
    static int CalculateMSTWeight()
    {
        int totalWeight = 0;
        for (int i = 0; i < n; i++)
        {
            if (parent[i] != -1)
            {
                totalWeight += graph[parent[i], i];
            }
        }
        return totalWeight;
    }
    static int[,] GenerateRandomGraph(int n)
    {
        Random rand = new Random(42);
        int[,] graph = new int[n, n];
        
        for (int i = 0; i < n; i++)
        {
            for (int j = i; j < n; j++)
            {
                if (i == j)
                    graph[i, j] = 0;
                else
                {
                    int weight = rand.NextDouble() < 0.7 ? rand.Next(1, 100) : INF;
                    graph[i, j] = weight;
                    graph[j, i] = weight; 
                }
            }
        }
        EnsureConnectivity(graph, rand);
        return graph;
    }

    static void EnsureConnectivity(int[,] graph, Random rand)
    {
        for (int i = 0; i < n - 1; i++)
        {
            if (graph[i, i + 1] == INF)
            {
                int weight = rand.Next(1, 100);
                graph[i, i + 1] = weight;
                graph[i + 1, i] = weight;
            }
        }
    }
    static long MeasureTime(Action action)
    {
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();

        Stopwatch sw = Stopwatch.StartNew();
        action();
        sw.Stop();
        return sw.ElapsedMilliseconds;
    }
}