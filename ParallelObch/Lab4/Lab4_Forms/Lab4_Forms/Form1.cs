using System;
using System.Collections.Concurrent;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;
using System.Diagnostics;

namespace Lab4_Forms
{
    public partial class Form1 : Form
    {
        private Panel[] cylinderContainers = new Panel[3];
        private Panel[] cylinders = new Panel[3];
        private Label[] labels = new Label[3];
        private Label[] statusLabels = new Label[3];
        private Button startButton;
        private Button stopButton;
        private Button restartButton;
        private Button randomButton;
        private Label infoLabel;

        private int[] initialTimes = { 500, 2000, 800 };
        private ConcurrentQueue<int>[] timeQueues = new ConcurrentQueue<int>[3];
        private Thread[] threads = new Thread[3];

        private long[] workTimeMs = new long[3];
        private long[] waitTimeMs = new long[3];

        private bool simulationRunning = false;
        private int cylinderHeight = 300;

        public Form1()
        {
            InitializeComponent();
            SetupForm();
            InitializeVisualization();

            for (int i = 0; i < 3; i++)
            {
                timeQueues[i] = new ConcurrentQueue<int>();
            }
        }

        private void SetupForm()
        {
            this.Text = "Візуалізація синхронізації потоків";
            this.Size = new Size(950, 650);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.BackColor = Color.WhiteSmoke;
        }

        private void InitializeVisualization()
        {
            for (int i = 0; i < 3; i++)
            {
                cylinderContainers[i] = new Panel();
                cylinderContainers[i].Location = new Point(70 + i * 170, 50);
                cylinderContainers[i].Size = new Size(110, cylinderHeight);
                cylinderContainers[i].BorderStyle = BorderStyle.FixedSingle;
                cylinderContainers[i].AutoScroll = true;
                cylinderContainers[i].BackColor = Color.White;
                this.Controls.Add(cylinderContainers[i]);

                cylinders[i] = new Panel();
                cylinders[i].Location = new Point(0, 0);
                cylinders[i].Size = new Size(90, 0); 
                cylinders[i].BackColor = Color.White; 
                cylinderContainers[i].Controls.Add(cylinders[i]);

                labels[i] = new Label();
                labels[i].Location = new Point(95 + i * 170, cylinderHeight + 60);
                labels[i].Size = new Size(60, 20);
                labels[i].Text = $"Потік {i + 1}";
                labels[i].TextAlign = ContentAlignment.MiddleCenter;
                labels[i].Font = new Font("Segoe UI", 9);
                this.Controls.Add(labels[i]);

                statusLabels[i] = new Label();
                statusLabels[i].Location = new Point(70 + i * 170, cylinderHeight + 85);
                statusLabels[i].Size = new Size(110, 40);
                statusLabels[i].Text = "Готовий";
                statusLabels[i].TextAlign = ContentAlignment.TopCenter;
                statusLabels[i].Font = new Font("Segoe UI", 8);
                statusLabels[i].BackColor = Color.White;
                statusLabels[i].BorderStyle = BorderStyle.FixedSingle;
                this.Controls.Add(statusLabels[i]);
            }

            startButton = new Button();
            startButton.Location = new Point(70, 440);
            startButton.Size = new Size(90, 30);
            startButton.Text = "Старт";
            startButton.FlatStyle = FlatStyle.Flat;
            startButton.Font = new Font("Segoe UI", 9);
            startButton.Click += StartButton_Click;
            this.Controls.Add(startButton);

            stopButton = new Button();
            stopButton.Location = new Point(170, 440);
            stopButton.Size = new Size(90, 30);
            stopButton.Text = "Стоп";
            stopButton.FlatStyle = FlatStyle.Flat;
            stopButton.Font = new Font("Segoe UI", 9);
            stopButton.Click += StopButton_Click;
            this.Controls.Add(stopButton);

            restartButton = new Button();
            restartButton.Location = new Point(270, 440);
            restartButton.Size = new Size(90, 30);
            restartButton.Text = "Заново";
            restartButton.FlatStyle = FlatStyle.Flat;
            restartButton.Font = new Font("Segoe UI", 9);
            restartButton.Click += RestartButton_Click;
            this.Controls.Add(restartButton);

            randomButton = new Button();
            randomButton.Location = new Point(370, 440);
            randomButton.Size = new Size(90, 30);
            randomButton.Text = "Випадково";
            randomButton.FlatStyle = FlatStyle.Flat;
            randomButton.Font = new Font("Segoe UI", 9);
            randomButton.Click += RandomButton_Click;
            this.Controls.Add(randomButton);

            infoLabel = new Label();
            infoLabel.Location = new Point(580, 50);
            infoLabel.Size = new Size(300, 380); 
            infoLabel.Font = new Font("Segoe UI", 9);
            infoLabel.BorderStyle = BorderStyle.FixedSingle;
            infoLabel.BackColor = Color.White;
            infoLabel.Padding = new Padding(10);
            UpdateInfoPanel();
            this.Controls.Add(infoLabel);
        }

        private void UpdateInfoPanel()
        {
            infoLabel.Text = $"ПОЧАТКОВІ ЧАСИ:\n\n" +
                             $"Потік 1 (t1,1): {initialTimes[0]} мс\n" +
                             $"Потік 2 (t2,1): {initialTimes[1]} мс\n" +
                             $"Потік 3 (t3,1): {initialTimes[2]} мс\n\n" +
                             $"Логіка роботи:\n" +
                             $"- Потік 1 → Потік 2\n" +
                             $"- Потік 2 → Потік 3\n" +
                             $"- Потік 3 → Потік 1\n\n";
        }

        private void StartButton_Click(object sender, EventArgs e)
        {
            if (simulationRunning) return;

            simulationRunning = true;
            startButton.Enabled = false;
            randomButton.Enabled = false;
            startButton.Text = "Виконується...";

            ClearCylinders();

            for (int i = 0; i < 3; i++)
            {
                while (timeQueues[i].TryDequeue(out _)) { }
                timeQueues[i].Enqueue(initialTimes[i]);
                workTimeMs[i] = 0;
                waitTimeMs[i] = 0;
                UpdateThreadStatus(i, "Початок", Color.LightYellow);
            }

            for (int i = 0; i < 3; i++)
            {
                int index = i;
                threads[i] = new Thread(() => ThreadWork(index));
                threads[i].IsBackground = true;
                threads[i].Start();
            }

            Thread timerThread = new Thread(() => {
                Thread.Sleep(20000);
                if (simulationRunning)
                {
                    Invoke(new Action(() => {
                        StopSimulation();
                    }));
                }
            });
            timerThread.IsBackground = true;
            timerThread.Start();
        }

        private void StopButton_Click(object sender, EventArgs e)
        {
            StopSimulation();
        }

        private void StopSimulation()
        {
            if (!simulationRunning) return;

            simulationRunning = false;
            startButton.Enabled = true;
            randomButton.Enabled = true;
            startButton.Text = "Старт";

            for (int i = 0; i < 3; i++)
            {
                ShowProductivity(i);
            }
        }

        private void RestartButton_Click(object sender, EventArgs e)
        {
            if (simulationRunning)
            {
                StopSimulation();
                Thread.Sleep(500);
            }

            ClearCylinders();
            for (int i = 0; i < 3; i++)
            {
                UpdateThreadStatus(i, "Готовий", Color.White);
            }

            StartButton_Click(sender, e);
        }

        private void ThreadWork(int threadIndex)
        {
            Random random = new Random(threadIndex * 1000 + Environment.TickCount);
            int cycle = 0;

            while (simulationRunning && cycle < 15)
            {
                int workTimeValue;

                Stopwatch waitStopwatch = new Stopwatch();
                waitStopwatch.Start();

                while (!timeQueues[threadIndex].TryDequeue(out workTimeValue))
                {
                    if (!simulationRunning) return;

                    this.Invoke((Action)(() => {
                        AddSegment(threadIndex, Color.Red, "W");
                        UpdateThreadStatus(threadIndex, $"Очікування\nчасу", Color.MistyRose);
                    }));

                    Thread.Sleep(100);
                }

                waitStopwatch.Stop();
                waitTimeMs[threadIndex] += waitStopwatch.ElapsedMilliseconds;

                if (!simulationRunning) break;

                this.Invoke((Action)(() => {
                    AddSegment(threadIndex, Color.RoyalBlue, workTimeValue.ToString());
                    UpdateThreadStatus(threadIndex, $"Робота\n{workTimeValue} мс\nЦикл {cycle + 1}", Color.AliceBlue);
                }));

                Thread.Sleep(workTimeValue);
                workTimeMs[threadIndex] += workTimeValue;

                if (!simulationRunning) break;

                int nextThreadIndex = (threadIndex + 1) % 3;
                int newTimeForNext = random.Next(500, 2000);
                //int newTimeForNext = initialTimes[nextThreadIndex];
                
                timeQueues[nextThreadIndex].Enqueue(newTimeForNext);

                this.Invoke((Action)(() => {
                    UpdateThreadStatus(threadIndex,
                        $"Надіслано {newTimeForNext}мс\nдо Потоку {nextThreadIndex + 1}",
                        Color.Honeydew);
                }));

                cycle++;
                Thread.Sleep(100);

                if (cycle >= 15 && simulationRunning)
                {
                    ShowProductivity(threadIndex);
                }
            }
        }

        private void ShowProductivity(int threadIndex)
        {
            this.Invoke((Action)(() => {
                long totalTime = workTimeMs[threadIndex] + waitTimeMs[threadIndex];
                double productivity = totalTime > 0 ? (double)workTimeMs[threadIndex] / totalTime * 100 : 0;

                AddSegment(threadIndex, Color.Orange, $"{productivity:F1}%");
                UpdateThreadStatus(threadIndex,
                    $"Завершено\nРобота: {workTimeMs[threadIndex]}мс\n" +
                    $"Продуктивність: {productivity:F1}%",
                    Color.Khaki);
            }));
        }

        private void AddSegment(int cylinderIndex, Color color, string text)
        {
            int segmentHeight = 20;

            Panel segment = new Panel();
            segment.Size = new Size(88, segmentHeight);
            segment.BackColor = color;
            segment.BorderStyle = BorderStyle.None;

            int yPos = cylinders[cylinderIndex].Height;
            segment.Location = new Point(1, yPos);

            Label label = new Label();
            label.Text = text;
            label.Size = new Size(86, segmentHeight);
            label.TextAlign = ContentAlignment.MiddleCenter;
            label.Font = new Font("Segoe UI", 7, FontStyle.Bold);
            label.ForeColor = (color == Color.RoyalBlue || color == Color.Orange) ? Color.White : Color.Black;
            label.BackColor = Color.Transparent;
            segment.Controls.Add(label);

            cylinders[cylinderIndex].Controls.Add(segment);
            cylinders[cylinderIndex].Height = yPos + segmentHeight;

            cylinderContainers[cylinderIndex].ScrollControlIntoView(segment);
        }

        private void UpdateThreadStatus(int threadIndex, string status, Color color)
        {
            statusLabels[threadIndex].Text = status;
            statusLabels[threadIndex].BackColor = color;
        }

        private void ClearCylinders()
        {
            for (int i = 0; i < 3; i++)
            {
                cylinders[i].Controls.Clear();
                cylinders[i].Height = 0;
                cylinders[i].BackColor = Color.White;
            }
        }

        private void RandomButton_Click(object sender, EventArgs e)
        {
            if (simulationRunning) return;

            Random random = new Random();
            for (int i = 0; i < 3; i++)
            {
                initialTimes[i] = random.Next(500, 2500);
            }

            UpdateInfoPanel();

            MessageBox.Show($"Згенеровано нові випадкові часи:\n\n" +
                          $"Потік 1 (t1,1): {initialTimes[0]} мс\n" +
                          $"Потік 2 (t2,1): {initialTimes[1]} мс\n" +
                          $"Потік 3 (t3,1): {initialTimes[2]} мс\n\n" +
                          $"Натисніть Старт щоб запустити з новими часами",
                          "Випадкові часи згенеровано",
                          MessageBoxButtons.OK,
                          MessageBoxIcon.Information);
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            simulationRunning = false;
            Thread.Sleep(300);
            base.OnFormClosed(e);
        }
    }
}