using System;
using System.Diagnostics;
using System.Threading;
using System.Linq;

class Program
{
    static int[,] A, B, Cseq, Cpar;
    static int n, m, p;
    static Thread[] threads;
    static long[] threadOperations;

    static void SeqMultiply()
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < p; j++)
            {
                int sum = 0;
                for (int x = 0; x < m; x++)
                {
                    sum += A[i, x] * B[x, j];
                }
                Cseq[i, j] = sum;
            }
        }
    }

    static void ParallelMultiply(int k)
    {
        threads = new Thread[k];
        threadOperations = new long[k];
        Cpar = new int[n, p];
        
        int rowsPerThread = n / k;
        int remainingRows = n % k;
        int startRow = 0;

        for (int t = 0; t < k; t++)
        {
            int rows = rowsPerThread;
            if (t < remainingRows)
            {
                rows += 1;
            }

            int sRow = startRow;
            int eRow = sRow + rows;
            int threadId = t;

            threads[t] = new Thread(() =>
            {
                long operations = 0;
                
                for (int i = sRow; i < eRow; i++)
                {
                    for (int j = 0; j < p; j++)
                    {
                        int sum = 0;
                        for (int x = 0; x < m; x++)
                        {
                            sum += A[i, x] * B[x, j];
                            operations++;
                        }
                        Cpar[i, j] = sum;
                    }
                }
                
                threadOperations[threadId] = operations;
            });
            
            threads[t].Start();
            startRow += rows;
        }

        foreach (var thread in threads)
        {
            thread.Join();
        }
    }

    static bool VerifyResults()
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < p; j++)
            {
                if (Cseq[i, j] != Cpar[i, j])
                {
                    return false;
                }
            }
        }
        return true;
    }

    static double MeasureTime(Action action, int runs = 3)
    {
        double bestTime = double.MaxValue;
        
        for (int run = 0; run < runs; run++)
        {
            var sw = Stopwatch.StartNew();
            action();
            sw.Stop();
            
            double time = sw.Elapsed.TotalMilliseconds;
            if (time < bestTime) bestTime = time;
        }
        
        return bestTime;
    }

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        
        Console.Write("Введіть кількість рядків матриці A: ");
        string input = Console.ReadLine();
        n = string.IsNullOrEmpty(input) ? 500 : int.Parse(input);
        
        Console.Write("Введіть кількість стовпців матриці A / рядків матриці B: ");
        input = Console.ReadLine();
        m = string.IsNullOrEmpty(input) ? 500 : int.Parse(input);
        
        Console.Write("Введіть кількість стовпців матриці B: ");
        input = Console.ReadLine();
        p = string.IsNullOrEmpty(input) ? 500 : int.Parse(input);
        
        Console.Write("Введіть максимальну кількість потоків для тестування: ");
        input = Console.ReadLine();
        int maxThreads = string.IsNullOrEmpty(input) ? Environment.ProcessorCount : int.Parse(input);

        A = new int[n, m];
        B = new int[m, p];
        Cseq = new int[n, p];

        Random rnd = new Random(42);
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < m; j++)
            {
                A[i, j] = rnd.Next(1, 101);
            }
        }
        for (int i = 0; i < m; i++)
        {
            for (int j = 0; j < p; j++)
            {
                B[i, j] = rnd.Next(1, 101);
            }
        }

        Console.WriteLine($"\n=== Розмір матриць ===");
        Console.WriteLine($"A: {n} × {m}");
        Console.WriteLine($"B: {m} × {p}");
        Console.WriteLine($"Кількість процесорів: {Environment.ProcessorCount}");
        Console.WriteLine($"Тестування до {maxThreads} потоків");

        Console.WriteLine("\nОбчислення послідовного множення...");
        double seqTime = MeasureTime(SeqMultiply);
        Console.WriteLine($"Час послідовного множення: {seqTime:F2} ms");

        Console.WriteLine("\n=== Результати тестування ===");
        Console.WriteLine("Потоки\tЧас (ms)\tПрискорення\tЕфективність");
        Console.WriteLine("".PadRight(50, '='));

        double bestTime = seqTime;
        int bestThreads = 1;
        Console.WriteLine($"1\t{seqTime:F2}\t\t1.00×\t\t100.0%");
        
        for (int k = 2; k <= maxThreads; k++)
        {
            double parTime = MeasureTime(() => ParallelMultiply(k));
            
            if (k == 2 && !VerifyResults())
            {
                Console.WriteLine("ПОМИЛКА: Результати не співпадають!");
                return;
            }
            
            double speedup = seqTime / parTime;
            double efficiency = speedup / k;
            
            Console.WriteLine($"{k}\t{parTime:F2}\t\t{speedup:F2}×\t\t{efficiency:P1}");
            
            if (parTime < bestTime)
            {
                bestTime = parTime;
                bestThreads = k;
            }
        }

        Console.WriteLine("\n=== Висновки ===");
        Console.WriteLine($"Найшвидша кількість потоків: {bestThreads}");
        Console.WriteLine($"Найкращий час: {bestTime:F2} ms");
        
        double bestSpeedup = seqTime / bestTime;
        Console.WriteLine($"Прискорення: {bestSpeedup:F2}×");
        Console.WriteLine($"Ефективність: {(bestSpeedup / bestThreads):P1}");

        Console.WriteLine("\n=== Аналіз паралелізації ===");
        double realP = (1 / bestSpeedup - 1) / (1.0 / bestThreads - 1);
        if (realP >= 0 && realP <= 1)
        {
            Console.WriteLine($"Оцінена паралельна частка: {realP:P1}");
            
            if (realP < 0.999)
            {
                double amdahlMax = 1.0 / (1.0 - realP);
                Console.WriteLine($"Теоретичний максимум прискорення: {amdahlMax:F2}×");
            }
        }   
        long totalOps = (long)n * m * p;
        Console.WriteLine($"Загальна кількість операцій множення: {totalOps:N0}");
    }
}