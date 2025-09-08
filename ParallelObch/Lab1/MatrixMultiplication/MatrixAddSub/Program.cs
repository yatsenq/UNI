using System;
using System.Diagnostics;
using System.Text;
using System.Threading.Tasks;

class Program
{
    static void PoslAddition(int[,] A, int[,] B, int[,] result)
    {
        int n = A.GetLength(0);
        int m = A.GetLength(1);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                result[i, j] = A[i, j] + B[i, j];
    }

    static void PoslSubstraction(int[,] A, int[,] B, int[,] result)
    {
        int n = A.GetLength(0);
        int m = A.GetLength(1);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                result[i, j] = A[i, j] - B[i, j];
    }

    static void ParallelAddition(int[,] A, int[,] B, int[,] C, int k)
    {
        int n = A.GetLength(0);
        int m = A.GetLength(1);
        int rowsPerTask = n / k;
        int remainingRows = n % k;
        Task[] tasks = new Task[k];
        int startRow = 0;

        for (int t = 0; t < k; t++)
        {
            int rows = rowsPerTask;
            if (t < remainingRows) rows += 1;
            int sRow = startRow;

            tasks[t] = Task.Run(() =>
            {
                for (int i = sRow; i < sRow + rows; i++)
                    for (int j = 0; j < m; j++)
                        C[i, j] = A[i, j] + B[i, j];
            });

            startRow += rows;
        }

        Task.WaitAll(tasks);
    }

    static void ParallelSubstraction(int[,] A, int[,] B, int[,] D, int k)
    {
        int n = A.GetLength(0);
        int m = A.GetLength(1);
        int rowsPerTask = n / k;
        int remainingRows = n % k;
        Task[] tasks = new Task[k];
        int startRow = 0;

        for (int t = 0; t < k; t++)
        {
            int rows = rowsPerTask;
            if (t < remainingRows) rows += 1;
            int sRow = startRow;

            tasks[t] = Task.Run(() =>
            {
                for (int i = sRow; i < sRow + rows; i++)
                    for (int j = 0; j < m; j++)
                        D[i, j] = A[i, j] - B[i, j];
            });

            startRow += rows;
        }

        Task.WaitAll(tasks);
    }

    static void DemoSmallAdd()
    {
        Console.WriteLine("Перевірка: додавання матриць 3×3");
        int[,] A = { { 1, 2, 3 }, { 4, 5, 6 }, { 7, 8, 9 } };
        int[,] B = { { 9, 8, 7 }, { 6, 5, 4 }, { 3, 2, 1 } };
        int[,] C = new int[3, 3];
        ParallelAddition(A, B, C, 2);

        Console.WriteLine("Матриця A:");
        PrintMatrix(A);
        Console.WriteLine("Матриця B:");
        PrintMatrix(B);
        Console.WriteLine("Результат C = A + B:");
        PrintMatrix(C);
        Console.WriteLine("---------------------------------------------\n");
    }

    static void PrintMatrix(int[,] M)
    {
        int n = M.GetLength(0);
        int m = M.GetLength(1);
        for (int i = 0; i < n; i++)
        {
            Console.Write("[ ");
            for (int j = 0; j < m; j++)
                Console.Write(M[i, j] + " ");
            Console.WriteLine("]");
        }
    }

    static int ReadInt(string prompt, int min = 1, int max = int.MaxValue)
    {
        while (true)
        {
            Console.Write(prompt);
            if (int.TryParse(Console.ReadLine(), out int value) && value >= min && value <= max)
                return value;
            Console.WriteLine($"Невірне значення. Дозволено: {min}..{max}");
        }
    }

    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;

        DemoSmallAdd();
        
        int n = ReadInt("Введіть кількість рядків (n): ", 1);
        int m = ReadInt("Введіть кількість стовпців (m): ", 1);
        int k = ReadInt($"Введіть кількість потоків (k, 1..{Environment.ProcessorCount * 2}): ",
                        1, Environment.ProcessorCount * 2);

        int[,] A = new int[n, m];
        int[,] B = new int[n, m];
        int[,] C = new int[n, m];
        int[,] D = new int[n, m];

        Random rnd = new Random();
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
            {
                A[i, j] = rnd.Next(0, 101);
                B[i, j] = rnd.Next(0, 101);
            }

        Stopwatch sw = new Stopwatch();

        sw.Start();
        PoslAddition(A, B, C);
        sw.Stop();
        double time_posl_add = sw.ElapsedMilliseconds;
        Console.WriteLine($"Час затрачений на ПОСЛІДОВНЕ додавання: {time_posl_add}ms");

        sw.Restart();
        ParallelAddition(A, B, C, k);
        sw.Stop();
        double time_parl_add = sw.ElapsedMilliseconds;
        Console.WriteLine($"Час затрачений на ПАРАЛЕЛЬНЕ додавання: {time_parl_add}ms");

        double speedup_add = time_posl_add / time_parl_add;
        double efficiency_add = speedup_add / k;
        Console.WriteLine($"Прискорення (додавання): {speedup_add:F2}x");
        Console.WriteLine($"Ефективність (додавання): {efficiency_add:P2}\n");

        sw.Restart();
        PoslSubstraction(A, B, C);
        sw.Stop();
        double time_posl_subs = sw.ElapsedMilliseconds;
        Console.WriteLine($"Час затрачений на ПОСЛІДОВНЕ віднімання: {time_posl_subs}ms");

        sw.Restart();
        ParallelSubstraction(A, B, D, k);
        sw.Stop();
        double time_parl_subs = sw.ElapsedMilliseconds;
        Console.WriteLine($"Час затрачений на ПАРАЛЕЛЬНЕ віднімання: {time_parl_subs}ms");

        double speedup_subs = time_posl_subs / time_parl_subs;
        double efficiency_subs = speedup_subs / k;
        Console.WriteLine($"Прискорення (віднімання): {speedup_subs:F2}x");
        Console.WriteLine($"Ефективність (віднімання): {efficiency_subs:P2}");
    }
}
