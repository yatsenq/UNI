using System;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;

class Program
{
    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new ThreadForm());
    }
}

class ThreadForm : Form
{
    private Panel cylinder1, cylinder2, cylinder3;
    private Button btnStart, btnExit;
    private CheckBox chkRandom;
    private TextBox txtT1, txtT2, txtT3;
    private Label lblStats;
    private volatile bool isRunning = false;

    private int nextT1, nextT2, nextT3;
    private bool t1Ready, t2Ready, t3Ready;
    private int finishedCount = 0;
    private readonly object lockObj = new object();

    // Статистика
    private int totalWorkTime1, totalWorkTime2, totalWorkTime3;
    private int totalWaitTime1, totalWaitTime2, totalWaitTime3;

    public ThreadForm()
    {
        Text = "Візуалізація 3-х потоків";
        Size = new Size(650, 600);
        StartPosition = FormStartPosition.CenterScreen;

        var lblT1 = new Label { Text = "T1 (мс):", Location = new Point(20, 15), AutoSize = true };
        txtT1 = new TextBox { Location = new Point(70, 12), Width = 60, Text = "1000" };

        var lblT2 = new Label { Text = "T2 (мс):", Location = new Point(150, 15), AutoSize = true };
        txtT2 = new TextBox { Location = new Point(200, 12), Width = 60, Text = "1500" };

        var lblT3 = new Label { Text = "T3 (мс):", Location = new Point(280, 15), AutoSize = true };
        txtT3 = new TextBox { Location = new Point(330, 12), Width = 60, Text = "800" };

        chkRandom = new CheckBox { Text = "Рандомні інтервали", Location = new Point(420, 14), AutoSize = true };
        chkRandom.CheckedChanged += (s, e) =>
        {
            txtT1.Enabled = !chkRandom.Checked;
            txtT2.Enabled = !chkRandom.Checked;
            txtT3.Enabled = !chkRandom.Checked;
        };

        cylinder1 = new Panel { Location = new Point(50, 80), Size = new Size(120, 300), BorderStyle = BorderStyle.FixedSingle, BackColor = Color.White };
        cylinder2 = new Panel { Location = new Point(230, 80), Size = new Size(120, 300), BorderStyle = BorderStyle.FixedSingle, BackColor = Color.White };
        cylinder3 = new Panel { Location = new Point(410, 80), Size = new Size(120, 300), BorderStyle = BorderStyle.FixedSingle, BackColor = Color.White };

        var lbl1 = new Label { Text = "Потік 1", Location = new Point(85, 390), AutoSize = true, Font = new Font("Arial", 10, FontStyle.Bold) };
        var lbl2 = new Label { Text = "Потік 2", Location = new Point(265, 390), AutoSize = true, Font = new Font("Arial", 10, FontStyle.Bold) };
        var lbl3 = new Label { Text = "Потік 3", Location = new Point(445, 390), AutoSize = true, Font = new Font("Arial", 10, FontStyle.Bold) };

        var lblLegend = new Label
        {
            Text = "Синій - Робота     Червоний - Очікування",
            Location = new Point(50, 50),
            AutoSize = true,
            ForeColor = Color.DarkBlue
        };

        lblStats = new Label
        {
            Location = new Point(20, 420),
            Size = new Size(600, 60),
        };

        btnStart = new Button { Text = "Старт", Location = new Point(50, 490), Size = new Size(100, 30), BackColor = Color.LightGreen };
        btnStart.Click += (s, e) => StartSimulation();

        btnExit = new Button { Text = "Вихід", Location = new Point(480, 490), Size = new Size(100, 30), BackColor = Color.LightCoral };
        btnExit.Click += (s, e) => Close();

        Controls.AddRange(new Control[] {
            lblT1, txtT1, lblT2, txtT2, lblT3, txtT3, chkRandom,
            lblLegend, cylinder1, cylinder2, cylinder3,
            lbl1, lbl2, lbl3, lblStats,
            btnStart, btnExit
        });
    }

    private void StartSimulation()
    {
        if (isRunning) return;

        cylinder1.Controls.Clear();
        cylinder2.Controls.Clear();
        cylinder3.Controls.Clear();

        isRunning = true;
        finishedCount = 0;
        btnStart.Enabled = false;

        totalWorkTime1 = totalWorkTime2 = totalWorkTime3 = 0;
        totalWaitTime1 = totalWaitTime2 = totalWaitTime3 = 0;

        if (chkRandom.Checked)
        {
            nextT1 = GetRandom();
            nextT2 = GetRandom();
            nextT3 = GetRandom();
        }
        else
        {
            nextT1 = int.Parse(txtT1.Text);
            nextT2 = int.Parse(txtT2.Text);
            nextT3 = int.Parse(txtT3.Text);
        }

        t1Ready = t2Ready = t3Ready = true;

        new Thread(() => WorkThread(1, cylinder1)).Start();
        new Thread(() => WorkThread(2, cylinder2)).Start();
        new Thread(() => WorkThread(3, cylinder3)).Start();
    }

    private void WorkThread(int id, Panel panel)
    {
        int myTime = 0;
        int myWorkTime = 0;
        int myWaitTime = 0;

        while (isRunning && GetTotalHeight(panel) < panel.Height - 2)
        {
            lock (lockObj)
            {
                if (id == 1 && t1Ready) { myTime = nextT1; t1Ready = false; }
                if (id == 2 && t2Ready) { myTime = nextT2; t2Ready = false; }
                if (id == 3 && t3Ready) { myTime = nextT3; t3Ready = false; }
            }

            // Робота
            AddSegment(panel, Color.Blue, 10);
            Thread.Sleep(myTime);
            myWorkTime += myTime;

            if (!isRunning || GetTotalHeight(panel) >= panel.Height - 10) break;

            // Передача черги
            int nextTime = chkRandom.Checked ? GetRandom() : myTime;
            lock (lockObj)
            {
                if (id == 1) { nextT2 = nextTime; t2Ready = true; }
                if (id == 2) { nextT3 = nextTime; t3Ready = true; }
                if (id == 3) { nextT1 = nextTime; t1Ready = true; }
            }

            // Очікування
            bool myReady = false;
            int waitStart = Environment.TickCount;
            while (!myReady && isRunning)
            {
                lock (lockObj)
                {
                    if (id == 1) myReady = t1Ready;
                    if (id == 2) myReady = t2Ready;
                    if (id == 3) myReady = t3Ready;
                }

                if (!myReady)
                {
                    AddSegment(panel, Color.Red, 3);
                    Thread.Sleep(100);
                }

                if (GetTotalHeight(panel) >= panel.Height - 5) break;
            }

            myWaitTime += Environment.TickCount - waitStart;
        }

        lock (lockObj)
        {
            if (id == 1) { totalWorkTime1 = myWorkTime; totalWaitTime1 = myWaitTime; }
            if (id == 2) { totalWorkTime2 = myWorkTime; totalWaitTime2 = myWaitTime; }
            if (id == 3) { totalWorkTime3 = myWorkTime; totalWaitTime3 = myWaitTime; }

            finishedCount++;
            if (finishedCount == 3)
                EndSimulation();
        }
    }

    private void AddSegment(Panel panel, Color color, int height)
    {
        if (panel.InvokeRequired)
        {
            panel.Invoke(new Action(() => AddSegment(panel, color, height)));
            return;
        }

        if (GetTotalHeight(panel) >= panel.Height - height) return;

        var segment = new Panel
        {
            BackColor = color,
            Height = height,
            Width = panel.Width - 2,
            Dock = DockStyle.Bottom
        };
        panel.Controls.Add(segment);
        segment.BringToFront();
    }

    private int GetTotalHeight(Panel panel)
    {
        int total = 0;
        foreach (Control c in panel.Controls)
            total += c.Height;
        return total;
    }

    private void EndSimulation()
    {
        if (InvokeRequired)
        {
            Invoke(new Action(EndSimulation));
            return;
        }

        isRunning = false;
        btnStart.Enabled = true;

        lblStats.Text = $"СТАТИСТИКА:\n" +
                       $"Потік 1: Робота={totalWorkTime1}мс  Очікування={totalWaitTime1}мс\n" +
                       $"Потік 2: Робота={totalWorkTime2}мс  Очікування={totalWaitTime2}мс\n" +
                       $"Потік 3: Робота={totalWorkTime3}мс  Очікування={totalWaitTime3}мс";
    }

    private int GetRandom() => new Random(Guid.NewGuid().GetHashCode()).Next(500, 2000);

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        isRunning = false;
        base.OnFormClosing(e);
    }
}
