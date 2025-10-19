using System;
using System.Diagnostics;
using System.Threading;
using System.Collections.Generic;

namespace FloydWarshall
{
    class Program
    {
        const int INF = int.MaxValue / 2;

        static void Main(string[] args)
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            
            bool continueProgram = true;

            while (continueProgram)
            {
                Console.Clear();

                Console.Write("Введіть розмір графа (n): ");
                int n = int.Parse(Console.ReadLine());

                Console.Write("Введіть максимальну кількість потоків: ");
                int maxThreads = int.Parse(Console.ReadLine());

                Console.Write("Введіть початкову вершину (0-{0}): ", n - 1);
                int startNode = int.Parse(Console.ReadLine());

                Console.Write("Введіть кінцеву вершину (0-{0}): ", n - 1);
                int endNode = int.Parse(Console.ReadLine());

                Console.WriteLine("\nОбчислення...\n");
                int[,] graph = GenerateRandomGraph(n);
                
                long sequentialTime = 0;
                long lastThreadTime = 0;
                long bestTime = long.MaxValue;
                int bestThreadCount = 1;
                double bestSpeedup = 1.0;
                double bestEfficiency = 100.0;
                int[,] finalResult = null;
                int[,] nextMatrix = null;
                int[,] originalGraph = null;
                
                Console.WriteLine("=====================================================================================");
                Console.WriteLine("||  Потоків    ||  Час виконання (мс)   ||   Прискорення   ||   Ефективність (%)   ||");
                Console.WriteLine("=====================================================================================");

                for (int threads = 1; threads <= maxThreads; threads++)
                {
                    int[,] resultGraph = (int[,])graph.Clone();
                    int[,] next = new int[n, n];
                    InitializeNextMatrix(next, n);
                    
                    long executionTime;
                    if (threads == 1)
                    {
                        executionTime = MeasureTime(() => FloydWarshallSequential(resultGraph, next));
                        sequentialTime = executionTime;
                        finalResult = resultGraph;
                        nextMatrix = next;
                        originalGraph = graph;
                    }
                    else
                    {
                        executionTime = MeasureTime(() => FloydWarshallParallel(resultGraph, next, threads));
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

                    if (threads == maxThreads)
                    {
                        lastThreadTime = executionTime;
                    }

                    if (threads == 1)
                    {
                        int distance = resultGraph[startNode, endNode];
                        Console.WriteLine("=====================================================================================");
                        if (distance == INF)
                        {
                            Console.WriteLine("Найкоротший шлях від вершини {0} до {1}: НЕ ІСНУЄ", startNode, endNode);
                        }
                        else
                        {
                            Console.WriteLine("Найкоротша відстань від вершини {0} до {1}: {2}", startNode, endNode, distance);
                            
                            List<int> path = ReconstructPath(startNode, endNode, nextMatrix);
                            if (path.Count > 0)
                            {
                                Console.WriteLine("Шлях ({0} вершин): {1}", path.Count, string.Join(" -> ", path));
                                Console.WriteLine();
                                Console.WriteLine("Деталі шляху з вагами:");
                                for (int i = 0; i < path.Count - 1; i++)
                                {
                                    int from = path[i];
                                    int to = path[i + 1];
                                    int weight = originalGraph[from, to];
                                    Console.WriteLine("Вершина {0} -> {1}: вага = {2}", from, to, weight);
                                }
                                Console.WriteLine();
                                Console.WriteLine("Загальна відстань: {0} (сума всіх ваг)", distance);
                                Console.WriteLine("=====================================================================================");
                                Console.WriteLine("||  Потоків    ||  Час виконання (мс)   ||   Прискорення   ||   Ефективність (%)   ||");
                                Console.WriteLine("=====================================================================================");

                            }
                        }
                    }
                }
                
                Console.WriteLine("\n=== Результати ===");
                Console.WriteLine("Розмір графа: {0} × {1} вершин", n, n);
                Console.WriteLine("Базовий час (1 потік): {0} мс", sequentialTime);
                Console.WriteLine("Максимальна кількість потоків: {0}", maxThreads);
                
                Console.WriteLine("\n=== Найкращий результат ===");
                Console.WriteLine("Оптимальна кількість потоків: {0}", bestThreadCount);
                Console.WriteLine("Час виконання: {0} мс", bestTime);
                Console.WriteLine("Прискорення: {0:F4}x", bestSpeedup);
                Console.WriteLine("Ефективність: {0:F2}%", bestEfficiency);

                Console.WriteLine("\n=== Час виконання ===");
                Console.WriteLine("Час виконання без потоків (1 потік): {0} мс", sequentialTime);
                Console.WriteLine("Час виконання з {0} потоками: {1} мс", maxThreads, lastThreadTime);

                Console.WriteLine("\n" + new string('─', 80));
                Console.Write("Бажаєте виконати ще один тест? (Y/N): ");
                string response = Console.ReadLine().Trim().ToUpper();
                continueProgram = (response == "Y" || response == "Т" || response == "YES");
            }
        }

        static void InitializeNextMatrix(int[,] next, int n)
        {
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    next[i, j] = -1;
                }
            }
        }

        static void FloydWarshallSequential(int[,] dist, int[,] next)
        {
            int n = dist.GetLength(0);

            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i != j && dist[i, j] != INF)
                    {
                        next[i, j] = j;
                    }
                }
            }

            for (int k = 0; k < n; k++)
            {
                for (int i = 0; i < n; i++)
                {
                    for (int j = 0; j < n; j++)
                    {
                        if (dist[i, k] != INF && dist[k, j] != INF)
                        {
                            int newDist = dist[i, k] + dist[k, j];
                            if (newDist < dist[i, j])
                            {
                                dist[i, j] = newDist;
                                next[i, j] = next[i, k];
                            }
                        }
                    }
                }
            }
        }

        static void FloydWarshallParallel(int[,] dist, int[,] next, int threadCount)
        {
            int n = dist.GetLength(0);

            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i != j && dist[i, j] != INF)
                    {
                        next[i, j] = j;
                    }
                }
            }

            for (int k = 0; k < n; k++)
            {
                Thread[] threads = new Thread[threadCount];
                int rowsPerThread = (n + threadCount - 1) / threadCount;

                for (int t = 0; t < threadCount; t++)
                {
                    int startRow = t * rowsPerThread;
                    int endRow = Math.Min(startRow + rowsPerThread, n);
                    int currentK = k;

                    threads[t] = new Thread(() =>
                    {
                        for (int i = startRow; i < endRow; i++)
                        {
                            for (int j = 0; j < n; j++)
                            {
                                if (dist[i, currentK] != INF && dist[currentK, j] != INF)
                                {
                                    int newDist = dist[i, currentK] + dist[currentK, j];
                                    if (newDist < dist[i, j])
                                    {
                                        dist[i, j] = newDist;
                                        next[i, j] = next[i, currentK];
                                    }
                                }
                            }
                        }
                    });
                    threads[t].Start();
                }
                foreach (Thread thread in threads)
                {
                    thread.Join();
                }
            }
        }

        static List<int> ReconstructPath(int start, int end, int[,] next)
        {
            List<int> path = new List<int>();
            
            if (next[start, end] == -1)
            {
                return path;
            }

            path.Add(start);
            int current = start;
            
            while (current != end)
            {
                current = next[current, end];
                if (current == -1)
                {
                    return new List<int>();
                }
                path.Add(current);
            }
            return path;
        }
        static int[,] GenerateRandomGraph(int n)
        {
            Random rand = new Random();
            int[,] graph = new int[n, n];

            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i == j)
                    {
                        graph[i, j] = 0;
                    }
                    else if (rand.NextDouble() < 0.7)
                    {
                        graph[i, j] = rand.Next(1, 100);
                    }
                    else
                    {
                        graph[i, j] = INF;
                    }
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
}