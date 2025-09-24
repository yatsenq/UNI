using System;
using System.Diagnostics;
using System.Threading;

class Program
{
    static double[,] A;
    static double[] b, xseq, xpar;
    static int n;
    static double epsilon = 1e-12;
    static int maxIter = 10000;

    static int JacobiSequential(double[,] A, double[] b, out double[] x)
    {
        int N = A.GetLength(0);
        x = new double[N];
        double[] xOld = new double[N];

        int iter = 0;
        while (iter < maxIter)
        {
            Array.Copy(x, xOld, N);
            for (int i = 0; i < N; i++)
            {
                double sum = 0;
                for (int j = 0; j < N; j++)
                    if (j != i) sum += A[i, j] * xOld[j];
                x[i] = (b[i] - sum) / A[i, i];
            }

            iter++;
            double maxDiff = 0;
            for (int i = 0; i < N; i++)
                maxDiff = Math.Max(maxDiff, Math.Abs(x[i] - xOld[i]));
            if (maxDiff < epsilon) break;
        }

        return iter;
    }

    public class ThreadData
    {
        public int StartRow { get; set; }
        public int EndRow { get; set; }
        public double[] XOld { get; set; }
        public double[] XNew { get; set; }
        public int ThreadId { get; set; }
    }

    static int JacobiParallel(int k)
    {
        int N = A.GetLength(0);
        double[] xOld = new double[N];
        double[] xNew = new double[N];
        //Array.Copy(b, xNew, N);

        ThreadData[] threadData = new ThreadData[k];

        int rowsPerThread = N / k;
        int extraRows = N % k;
        int currentStart = 0;

        for (int t = 0; t < k; t++)
        {
            int rows = rowsPerThread + (t < extraRows ? 1 : 0);

            threadData[t] = new ThreadData
            {
                StartRow = currentStart,
                EndRow = currentStart + rows,
                ThreadId = t
            };

            currentStart += rows;
        }

        int iter = 0;
        while (iter < maxIter)
        {
            Array.Copy(xNew, xOld, N);

            Thread[] threads = new Thread[k];

            for (int t = 0; t < k; t++)
            {
                threadData[t].XOld = xOld;
                threadData[t].XNew = xNew;

                ThreadData data = threadData[t];

                threads[t] = new Thread(() => WorkerThread(data));
                threads[t].Start();
            }

            for (int t = 0; t < k; t++)
                threads[t].Join();

            double maxDiff = 0;
            for (int i = 0; i < N; i++)
                maxDiff = Math.Max(maxDiff, Math.Abs(xNew[i] - xOld[i]));

            if (maxDiff < epsilon) break;
            iter++;
        }

        xpar = xNew;
        return iter;
    }

    static void WorkerThread(ThreadData data)
    {
        int N = A.GetLength(0);

        for (int i = data.StartRow; i < data.EndRow; i++)
        {
            double sum = 0;
            double aii = A[i, i];

            for (int j = 0; j < i; j++)
                sum += A[i, j] * data.XOld[j];
            for (int j = i + 1; j < N; j++)
                sum += A[i, j] * data.XOld[j];

            data.XNew[i] = (b[i] - sum) / aii;
        }
    }

    static bool Verify()
    {
        for (int i = 0; i < n; i++)
            if (Math.Abs(xseq[i] - xpar[i]) > epsilon) return false;
        return true;
    }

    static (double Time, int Iterations) MeasureTime(Func<int> action, int runs = 3)
    {
        double best = double.MaxValue;
        int iterations = 0;
        
        for (int r = 0; r < runs; r++)
        {
            var sw = Stopwatch.StartNew();
            int iter = action();
            sw.Stop();
            
            if (sw.Elapsed.TotalMilliseconds < best)
            {
                best = sw.Elapsed.TotalMilliseconds;
                iterations = iter;
            }
        }
        
        return (best, iterations);
    }

    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;

        Console.Write("Введіть розмір матриці (за замовчуванням 1000): ");
        string inp = Console.ReadLine();
        n = string.IsNullOrEmpty(inp) ? 1000 : int.Parse(inp);

        Console.Write("Введіть макс. кількість потоків: ");
        inp = Console.ReadLine();
        int maxThreads = string.IsNullOrEmpty(inp) ? Environment.ProcessorCount : int.Parse(inp);

        Console.WriteLine("\nВиберіть рівень діагональної домінантності:");
        Console.WriteLine("1 - Слабка (може не збігатися)");
        Console.WriteLine("2 - Середня (збіжність за ~100-500 ітерацій)");
        Console.WriteLine("3 - Сильна (швидка збіжність за ~10-50 ітерацій)");
        Console.Write("Ваш вибір (за замовчуванням 2): ");
        inp = Console.ReadLine();
        int domLevel = string.IsNullOrEmpty(inp) ? 2 : int.Parse(inp);

        A = new double[n, n];
        b = new double[n];
        Random rnd = new Random(42);

        Console.WriteLine($"\nСтворюємо матриця {n}×{n} з рівнем домінантності {domLevel}...");
        var sw = Stopwatch.StartNew();

        double offDiagScale, diagMultiplier, diagBonus;
        switch (domLevel)
        {
            case 1: 
                offDiagScale = 0.9;
                diagMultiplier = 1.1;
                diagBonus = 0.5;
                break;
            case 3: 
                offDiagScale = 0.3;
                diagMultiplier = 3.0;
                diagBonus = 10.0;
                break;
            default: 
                offDiagScale = 0.6;
                diagMultiplier = 1.8;
                diagBonus = 3.0;
                break;
        }

        for (int i = 0; i < n; i++)
        {
            double rowSum = 0;
            for (int j = 0; j < n; j++)
            {
                if (i != j)
                {
                    A[i, j] = rnd.NextDouble() * offDiagScale;
                    rowSum += Math.Abs(A[i, j]);
                }
            }
            A[i, i] = rowSum * diagMultiplier + diagBonus + rnd.NextDouble();
            b[i] = rnd.Next(1, 20);
        }

        sw.Stop();
        Console.WriteLine($"Матриця створена за {sw.ElapsedMilliseconds} ms");
        Console.WriteLine($"\nМатриця: {n}×{n}, CPU: {Environment.ProcessorCount}, тестуємо до {maxThreads} потоків");

        var seqResult = MeasureTime(() => JacobiSequential(A, b, out xseq));
        double seqTime = seqResult.Time;
        int seqIterations = seqResult.Iterations;
        
        Console.WriteLine($"\nЧас послідовного: {seqTime:F2} ms, ітерацій: {seqIterations}\n");

        Console.WriteLine("=== Результати паралельного обчислення ===");
        Console.WriteLine($"{"Потоки",-8}{"Час (ms)",-14}{"Прискорення",-15}{"Ефективність",-15}{"Ітерації"}");
        Console.WriteLine(new string('=', 70));

        double bestTime = seqTime;
        int bestThreads = 1;
        
        Console.WriteLine($"1{"",6}{seqTime:F2}{"",6}1.00×{"",5}100%{"",10}{seqIterations}");

        for (int k = 2; k <= maxThreads; k++)
        {
            var parResult = MeasureTime(() => JacobiParallel(k));
            double parTime = parResult.Time;
            int parIterations = parResult.Iterations;

            if (k == 2 && !Verify())
            {
                Console.WriteLine("ПОМИЛКА: результати не співпадають!");
                return;
            }

            double speedup = seqTime / parTime;
            double eff = speedup / k * 100;

            Console.WriteLine($"{k,-8}{parTime,-14:F2}{speedup,-15:F2}{eff:F1}%{"",10}{parIterations}");

            if (parTime < bestTime)
            {
                bestTime = parTime;
                bestThreads = k;
            }
        }

        Console.WriteLine("\n=== Висновок ===");
        Console.WriteLine($"Найкраща кількість потоків: {bestThreads}");
        Console.WriteLine($"Найшвидший час: {bestTime:F2} ms");
        Console.WriteLine($"Прискорення: {seqTime / bestTime:F2}×");
        Console.WriteLine($"Ефективність: {(seqTime / bestTime / bestThreads * 100):F1}%");
    }
}