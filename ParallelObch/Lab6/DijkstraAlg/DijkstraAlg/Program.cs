using System;
using System.Diagnostics;
using System.Threading;
using System.Collections.Generic;

class DijkstraParallel
{
    static int n;
    static int maxThreads;
    static int[,] graph;
    static int source;
    static int[] parent;
    static Barrier barrier; 

    const int INF = int.MaxValue / 2;

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        
        bool continueProgram = true;

        while (continueProgram)
        {
            Console.Clear();

            Console.Write("Введіть розмір графа (n): ");
            n = int.Parse(Console.ReadLine());

            Console.Write("Введіть максимальну кількість потоків: ");
            maxThreads = int.Parse(Console.ReadLine());

            Console.Write("Введіть стартову вершину (0 до " + (n - 1) + "): ");
            source = int.Parse(Console.ReadLine());

            if (source < 0 || source >= n)
            {
                Console.WriteLine("Помилка: вершина повинна бути від 0 до " + (n - 1));
                Console.ReadKey();
                continue;
            }

            Console.WriteLine("\nОбчислення...\n");
            graph = GenerateRandomGraph(n);
            
            long sequentialTime = 0;
            long bestTime = long.MaxValue;
            int bestThreadCount = 1;
            double bestSpeedup = 1.0;
            double bestEfficiency = 100.0;

            Console.WriteLine("=====================================================================================");
            Console.WriteLine("||  Потоків    ||  Час виконання (мс)   ||   Прискорення   ||   Ефективність (%)   ||");
            Console.WriteLine("=====================================================================================");

            for (int threads = 1; threads <= maxThreads; threads++)
            {
                int[] resultDist = new int[n];
                parent = new int[n];
                barrier = new Barrier(threads);
                
                long executionTime;
                if (threads == 1)
                {
                    executionTime = MeasureTime(() => DijkstraSequentialWithParent(resultDist));
                    sequentialTime = executionTime;
                }
                else
                {
                    executionTime = MeasureTime(() => DijkstraParallelMethod(resultDist, threads));
                }

                double speedup = (double)sequentialTime / executionTime;
                double efficiency = (speedup / threads) * 100.0;

                if (executionTime < bestTime)
                {
                    bestTime = executionTime;
                    bestThreadCount = threads;
                    bestSpeedup = speedup;
                    bestEfficiency = efficiency;
                }

                Console.WriteLine("|| {0,11} || {1,21} || {2,15:F4} || {3,20:F2}% ||",
                    threads, executionTime, speedup, efficiency);

                if (threads == 1)
                {
                    Console.WriteLine("=====================================================================================");
                    Console.WriteLine("Найкоротші відстані від вершини {0} до всіх інших вершин:", source);
                    Console.WriteLine();
                    
                    int displayCount = Math.Min(3, n);
                    for (int i = 0; i < displayCount; i++)
                    {
                        if (resultDist[i] == INF)
                            Console.WriteLine("a{0} -> a{1}: НЕ ІСНУЄ", source, i);
                        else
                            Console.WriteLine("a{0} -> a{1}: {2}", source, i, resultDist[i]);
                    }
                    
                    if (n > 3)
                        Console.WriteLine("... та ще {0} вершин", n - 3);
                    
                    Console.WriteLine("=====================================================================================");
                    Console.WriteLine("||  Потоків    ||  Час виконання (мс)   ||   Прискорення   ||   Ефективність (%)   ||");
                    Console.WriteLine("=====================================================================================");
                }
            }

            Console.WriteLine("\n============ Результати ===============");
            Console.WriteLine("Розмір графа: {0} × {0} вершин", n);
            Console.WriteLine("Базовий час (1 потік): {0} мс", sequentialTime);
            Console.WriteLine("Максимальна кількість потоків: {0}", maxThreads);
            
            Console.WriteLine("\n============== Найкращий результат ================");
            Console.WriteLine("Оптимальна кількість потоків: {0}", bestThreadCount);
            Console.WriteLine("Час виконання: {0} мс", bestTime);
            Console.WriteLine("Прискорення: {0:F4}x", bestSpeedup);
            Console.WriteLine("Ефективність: {0:F2}%", bestEfficiency);

            Console.WriteLine("\n================ Час виконання ===================");
            Console.WriteLine("Час виконання без потоків (1 потік): {0} мс", sequentialTime);
            Console.WriteLine("Час виконання з найкращим результатом ({0} потоків): {1} мс", bestThreadCount, bestTime);

            Console.WriteLine("\n" + new string('─', 80));
            Console.Write("Бажаєте виконати ще один тест? (Y/N): ");
            string response = Console.ReadLine().Trim().ToUpper();
            continueProgram = (response == "Y" || response == "Т" || response == "YES");
        }
    }

    static void DijkstraSequentialWithParent(int[] dist)
    {
        for (int i = 0; i < n; i++)
        {
            dist[i] = INF;
            parent[i] = -1;
        }
        dist[source] = 0;
        bool[] visited = new bool[n];

        for (int count = 0; count < n - 1; count++)
        {
            int u = MinDistance(dist, visited);
            if (u == -1) break;
            visited[u] = true;

            for (int v = 0; v < n; v++)
            {
                if (!visited[v] && graph[u, v] != INF && dist[u] != INF &&
                    dist[u] + graph[u, v] < dist[v])
                {
                    dist[v] = dist[u] + graph[u, v];
                    parent[v] = u;
                }
            }
        }
    }

    static void DijkstraParallelMethod(int[] dist, int numThreads)
    {
        for (int i = 0; i < n; i++)
        {
            dist[i] = INF;
            parent[i] = -1;
        }
        dist[source] = 0;
        bool[] visited = new bool[n];

        Thread[] threads = new Thread[numThreads];
        int rowsPerThread = n / numThreads;

        for (int t = 0; t < numThreads; t++)
        {
            int start = t * rowsPerThread;
            int end = (t == numThreads - 1) ? n : start + rowsPerThread;

            threads[t] = new Thread(() =>
            {
                for (int step = 0; step < n - 1; step++)
                {
                    int u = MinDistance(dist, visited);
                    barrier.SignalAndWait();

                    if (u == -1) continue;
                    visited[u] = true;

                    for (int v = start; v < end; v++)
                    {
                        if (!visited[v] && graph[u, v] != INF && dist[u] != INF)
                        {
                            int newDist = dist[u] + graph[u, v];
                            if (newDist < dist[v])
                            {
                                dist[v] = newDist;
                                parent[v] = u;
                            }
                        }
                    }
                    barrier.SignalAndWait();
                }
            });
            threads[t].Start();
        }
        foreach (Thread t in threads)
            t.Join();
    }
    static int MinDistance(int[] dist, bool[] visited)
    {
        int min = INF, minIndex = -1;
        for (int v = 0; v < n; v++)
        {
            if (!visited[v] && dist[v] <= min)
            {
                min = dist[v];
                minIndex = v;
            }
        }
        return minIndex;
    }

    static int[,] GenerateRandomGraph(int n)
    {
        Random rand = new Random(0);
        int[,] graph = new int[n, n];
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                if (i == j)
                    graph[i, j] = 0;
                else
                    graph[i, j] = rand.NextDouble() < 0.7 ? rand.Next(1, 100) : INF;
            }
        }
        return graph;
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