using System;
using System.Diagnostics;
using System.Threading;

class Program
{
    static int[,] A, B, Cseq, Cpar;
    static int n, m, p, k;
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

    static void ParlMultiply()
    {
        threads = new Thread[k];
        threadOperations = new long[k];
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

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.Write("Введіть кількість рядків матриці A: ");
        n = int.Parse(Console.ReadLine() ?? "0");
        Console.Write("Введіть кількість стовпців матриці A / рядків матриці B: ");
        m = int.Parse(Console.ReadLine() ?? "0");
        Console.Write("Введіть кількість стовпців матриці B: ");
        p = int.Parse(Console.ReadLine() ?? "0");
        Console.Write("Введіть кількість потоків k: ");
        k = int.Parse(Console.ReadLine() ?? "1");

        A = new int[n, m];
        B = new int[m, p];
        Cseq = new int[n, p];
        Cpar = new int[n, p];

        Random rnd = new Random();
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

        Console.WriteLine("\n=== Розмір матриць ===");
        Console.WriteLine($"A: {n} × {m}");
        Console.WriteLine($"B: {m} × {p}");
        Console.WriteLine($"Потоків: {k}");

        int baseRows = n / k;
        int extraRows = n % k;
        Console.WriteLine($"\nРозподіл рядків: {baseRows} базових + {extraRows} додаткових");

        const int runs = 3;
        double bestSeqTime = double.MaxValue;
        double bestParTime = double.MaxValue;
        
        Console.WriteLine($"\nВиконання {runs} прогонів для найкращого результату...");
        
        for (int run = 1; run <= runs; run++)
        {
            Console.WriteLine($"Прогон {run}/{runs}:");
            
            var sw = Stopwatch.StartNew();
            SeqMultiply();
            sw.Stop();
            double tSeq = sw.Elapsed.TotalMilliseconds;
            if (tSeq < bestSeqTime) bestSeqTime = tSeq;
            
            sw.Restart();
            ParlMultiply();
            sw.Stop();
            double tPar = sw.Elapsed.TotalMilliseconds;
            if (tPar < bestParTime) bestParTime = tPar;
            
            Console.WriteLine($"  Послідовно: {tSeq:F2} ms, Паралельно: {tPar:F2} ms");
            
            if (run == 1)
            {
                if (!VerifyResults())
                {
                    Console.WriteLine("ПОМИЛКА: Результати не співпадають!");
                    return;
                }
            }
        }

        Console.WriteLine($"\nНайкращі результати:");
        Console.WriteLine($"Час послідовного множення: {bestSeqTime:F2} ms");
        Console.WriteLine($"Час паралельного множення: {bestParTime:F2} ms");
        Console.WriteLine("Результати співпадають");
        
        long totalOperations = threadOperations.Sum();
        Console.WriteLine($"\nСтатистика операцій:");
        Console.WriteLine($"Загальна кількість операцій: {totalOperations:N0}");
        for (int i = 0; i < k; i++)
        {
            Console.WriteLine($"Потік {i + 1}: {threadOperations[i]:N0} операцій");
        }
        
        double speedup = bestSeqTime / bestParTime;
        double efficiency = speedup / k;
        double theoreticalMax = k;  
        
        Console.WriteLine($"\nПрискорення: {speedup:F2}×");
        Console.WriteLine($"Теоретичний максимум: {theoreticalMax:F2}×");
        Console.WriteLine($"Ефективність: {efficiency:P1}");

        double realP = (1 / speedup - 1) / (1.0 / k - 1);
        if (realP >= 0 && realP <= 1)
        {
            Console.WriteLine($"Реальна паралельна частка P ≈ {realP:P1}");
            
            if (realP < 0.999)
            {
                double amdahlMax = 1.0 / (1.0 - realP);
                Console.WriteLine($"Максимум прискорення за Амдалем (∞ потоків): {amdahlMax:F2}×");
            }
            else
            {
                Console.WriteLine($"Максимум прискорення за Амдалем (∞ потоків): >1000× (майже ідеальна паралелізація)");
            }
        }
    }
}