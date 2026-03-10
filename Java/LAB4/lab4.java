import java.awt.BasicStroke;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridLayout;
import java.awt.RenderingHints;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSlider;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;

public class lab4 extends JFrame {
    private AnimationThread animationThread; // потоки
    private CalculationThread calculationThread;
    private ScrollingThread scrollingThread;
    
    private AnimationPanel animationPanel;
    private JTextArea calculationArea;
    private ScrollingPanel scrollingPanel;
    private JTextArea priorityTestArea = new JTextArea();
    
    private final Lock sharedLock = new ReentrantLock(); // блокувальник
    private final Condition condition = sharedLock.newCondition();
    
    public lab4() {
        setTitle("Багатопоточне програмування");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));
        
        JPanel mainPanel = new JPanel(new GridLayout(1, 3, 10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        
        mainPanel.add(createAnimationSection());
        mainPanel.add(createCalculationSection());
        mainPanel.add(createScrollingSection());
        
        add(mainPanel, BorderLayout.CENTER);
        add(createControlPanel(), BorderLayout.SOUTH);
        
        setSize(1200, 600);
        setLocationRelativeTo(null);
    }
    
    private void runPriorityTest() {
    priorityTestArea.setText("");
    priorityTestArea.append("Запуск тесту пріоритетів...\n");

    class BusyThread extends Thread {
        public long counter = 0;
        private boolean slowMode;

        public BusyThread(int priority, boolean slowMode) {
            this.slowMode = slowMode;
            setPriority(priority);
        }

        @Override
        public void run() {
            while (!isInterrupted()) {
                counter++;

                if (slowMode) {
                    for (int i = 0; i < 500; i++) {
                        Math.sqrt(i * 123.456);
                    }
                }
            }
        }
    }

    BusyThread low = new BusyThread(Thread.MIN_PRIORITY, true);   
    BusyThread high = new BusyThread(Thread.MAX_PRIORITY, false); 

    low.start();
    high.start();

    new Thread(() -> {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {}

        low.interrupt();
        high.interrupt();

        priorityTestArea.append("LOW priority count = " + low.counter + "\n");
        priorityTestArea.append("HIGH priority count = " + high.counter + "\n");

        if (high.counter > low.counter) {
            priorityTestArea.append("\nПріоритет працює\n");
        } else {
            priorityTestArea.append("\nПріоритет мінімальний\n");
        }

    }).start();
}



    private JPanel createAnimationSection() {
        JPanel panel = new JPanel(new BorderLayout(5, 5));
        panel.setBorder(BorderFactory.createTitledBorder("Потік 1: Анімація"));
        
        animationPanel = new AnimationPanel();
        animationPanel.setBackground(Color.WHITE);
        panel.add(animationPanel, BorderLayout.CENTER);
        
        JPanel controls = new JPanel(new GridLayout(4, 1, 5, 5));
        
        JButton startBtn = new JButton("Старт");
        JButton pauseBtn = new JButton("Пауза");
        
        JSlider prioritySlider = new JSlider(1, 10, 5);
        prioritySlider.setBorder(BorderFactory.createTitledBorder("Пріоритет"));
        prioritySlider.setMajorTickSpacing(1);
        prioritySlider.setPaintTicks(true);
        prioritySlider.setPaintLabels(true);
        
        JSlider speedSlider = new JSlider(10, 100, 50);
        speedSlider.setBorder(BorderFactory.createTitledBorder("Швидкість"));
        
        startBtn.addActionListener(e -> {
            if (animationThread == null || !animationThread.isAlive()) {
                animationThread = new AnimationThread();
                animationThread.setPriority(prioritySlider.getValue());
                animationThread.start();
            }
            animationThread.resumeThread();
        });
        
        pauseBtn.addActionListener(e -> {
            if (animationThread != null) animationThread.pauseThread();
        });
        
        prioritySlider.addChangeListener(e -> {
            if (animationThread != null && animationThread.isAlive()) {
                animationThread.setPriority(prioritySlider.getValue());
            }
        });
        
        speedSlider.addChangeListener(e -> {
            if (animationThread != null) animationThread.setSpeed(speedSlider.getValue());
        });
        
        JPanel btnPanel = new JPanel(new GridLayout(1, 2, 5, 0));
        btnPanel.add(startBtn);
        btnPanel.add(pauseBtn);
        
        controls.add(btnPanel);
        controls.add(prioritySlider);
        controls.add(speedSlider);
        
        panel.add(controls, BorderLayout.SOUTH);
        return panel;
    }
    
    private JPanel createCalculationSection() {
        JPanel panel = new JPanel(new BorderLayout(5, 5));
        panel.setBorder(BorderFactory.createTitledBorder("Потік 2: Обчислення"));
        
        calculationArea = new JTextArea();
        calculationArea.setEditable(false);
        calculationArea.setFont(new Font("Monospaced", Font.PLAIN, 11));
        JScrollPane scrollPane = new JScrollPane(calculationArea);
        panel.add(scrollPane, BorderLayout.CENTER);
        
        JPanel controls = new JPanel(new GridLayout(4, 1, 5, 5));
        
        JButton startBtn = new JButton("Старт");
        JButton pauseBtn = new JButton("Пауза");
        
        JSlider prioritySlider = new JSlider(1, 10, 5);
        prioritySlider.setBorder(BorderFactory.createTitledBorder("Пріоритет"));
        prioritySlider.setMajorTickSpacing(1);
        prioritySlider.setPaintTicks(true);
        prioritySlider.setPaintLabels(true);
        
        JSlider delaySlider = new JSlider(100, 2000, 500);
        delaySlider.setBorder(BorderFactory.createTitledBorder("Затримка (мс)"));
        
        startBtn.addActionListener(e -> {
            if (calculationThread == null || !calculationThread.isAlive()) {
                calculationThread = new CalculationThread();
                calculationThread.setPriority(prioritySlider.getValue());
                calculationThread.start();
            }
            calculationThread.resumeThread();
        });
        
        pauseBtn.addActionListener(e -> {
            if (calculationThread != null) calculationThread.pauseThread();
        });
        
        prioritySlider.addChangeListener(e -> {
            if (calculationThread != null && calculationThread.isAlive()) {
                calculationThread.setPriority(prioritySlider.getValue());
            }
        });
        
        delaySlider.addChangeListener(e -> {
            if (calculationThread != null) calculationThread.setDelay(delaySlider.getValue());
        });
        
        JPanel btnPanel = new JPanel(new GridLayout(1, 2, 5, 0));
        btnPanel.add(startBtn);
        btnPanel.add(pauseBtn);
        
        controls.add(btnPanel);
        controls.add(prioritySlider);
        controls.add(delaySlider);
        
        panel.add(controls, BorderLayout.SOUTH);
        return panel;
    }
    
    private JPanel createScrollingSection() {
        JPanel panel = new JPanel(new BorderLayout(5, 5));
        panel.setBorder(BorderFactory.createTitledBorder("Потік 3: Біжучий рядок"));
        
        scrollingPanel = new ScrollingPanel();
        scrollingPanel.setBackground(new Color(240, 240, 250));
        panel.add(scrollingPanel, BorderLayout.CENTER);
        
        JPanel controls = new JPanel(new GridLayout(5, 1, 5, 5));
        
        JButton startBtn = new JButton("Старт");
        JButton pauseBtn = new JButton("Пауза");
        
        JTextField textField = new JTextField("Багатопоточне програмування в Java");
        
        JSlider prioritySlider = new JSlider(1, 10, 5);
        prioritySlider.setBorder(BorderFactory.createTitledBorder("Пріоритет"));
        prioritySlider.setMajorTickSpacing(1);
        prioritySlider.setPaintTicks(true);
        prioritySlider.setPaintLabels(true);
        
        JSlider speedSlider = new JSlider(1, 20, 5);
        speedSlider.setBorder(BorderFactory.createTitledBorder("Швидкість"));
        
        startBtn.addActionListener(e -> {
            if (scrollingThread == null || !scrollingThread.isAlive()) {
                scrollingThread = new ScrollingThread();
                scrollingThread.setPriority(prioritySlider.getValue());
                scrollingThread.start();
            }
            scrollingThread.resumeThread();
        });
        
        pauseBtn.addActionListener(e -> {
            if (scrollingThread != null) scrollingThread.pauseThread();
        });
        
        textField.addActionListener(e -> {
            if (scrollingThread != null) scrollingPanel.setText(textField.getText());
        });
        
        prioritySlider.addChangeListener(e -> {
            if (scrollingThread != null && scrollingThread.isAlive()) {
                scrollingThread.setPriority(prioritySlider.getValue());
            }
        });
        
        speedSlider.addChangeListener(e -> {
            if (scrollingThread != null) scrollingPanel.setSpeed(speedSlider.getValue());
        });
        
        JPanel btnPanel = new JPanel(new GridLayout(1, 2, 5, 0));
        btnPanel.add(startBtn);
        btnPanel.add(pauseBtn);
        
        controls.add(btnPanel);
        controls.add(textField);
        controls.add(prioritySlider);
        controls.add(speedSlider);
        
        panel.add(controls, BorderLayout.SOUTH);
        return panel;
    }
    
    private JPanel createControlPanel() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 10));
        panel.setBorder(BorderFactory.createTitledBorder("Загальне керування"));
        
        JButton startAllBtn = new JButton("Запустити всі");
        JButton pauseAllBtn = new JButton("Призупинити всі");
        JButton stopAllBtn = new JButton("Зупинити всі");
        JButton syncBtn = new JButton("Синхронізація");
        
        startAllBtn.addActionListener(e -> {
            if (animationThread == null || !animationThread.isAlive()) {
                animationThread = new AnimationThread();
                animationThread.start();
            }
            if (calculationThread == null || !calculationThread.isAlive()) {
                calculationThread = new CalculationThread();
                calculationThread.start();
            }
            if (scrollingThread == null || !scrollingThread.isAlive()) {
                scrollingThread = new ScrollingThread();
                scrollingThread.start();
            }
            animationThread.resumeThread();
            calculationThread.resumeThread();
            scrollingThread.resumeThread();
        });
        
        pauseAllBtn.addActionListener(e -> {
            if (animationThread != null) animationThread.pauseThread();
            if (calculationThread != null) calculationThread.pauseThread();
            if (scrollingThread != null) scrollingThread.pauseThread();
        });
        
        stopAllBtn.addActionListener(e -> {
            if (animationThread != null) {
                animationThread.stopThread();
                animationThread = null;
            }
            if (calculationThread != null) {
                calculationThread.stopThread();
                calculationThread = null;
            }
            if (scrollingThread != null) {
                scrollingThread.stopThread();
                scrollingThread = null;
            }
            
            animationPanel.reset();
            calculationArea.setText("");
            scrollingPanel.reset();
        });
        
        syncBtn.addActionListener(e -> demonstrateSynchronization());
        
        panel.add(startAllBtn);
        panel.add(pauseAllBtn);
        panel.add(stopAllBtn);
        panel.add(syncBtn);
        
        JButton priorityTestBtn = new JButton("Тест пріоритетів");
        priorityTestBtn.addActionListener(e -> runPriorityTest());
        panel.add(priorityTestBtn);
        priorityTestArea.setColumns(75);
        priorityTestArea.setRows(12); 
        priorityTestArea.setFont(new Font("Monospaced", Font.BOLD, 20));
        priorityTestArea.setEditable(false);
        panel.add(new JScrollPane(priorityTestArea));


        return panel;
    }
    
    private void demonstrateSynchronization() { // синхронізація
        new Thread(() -> {
            JOptionPane.showMessageDialog(this, 
                "Потік анімації буде заблоковано на 3 секунди\n" +
                "під час виконання критичної секції обчислень.",
                "Синхронізація", JOptionPane.INFORMATION_MESSAGE);
            
            if (calculationThread != null && animationThread != null) {
                sharedLock.lock();
                try {
                    calculationArea.append("\n>>> БЛОКУВАННЯ АНІМАЦІЇ <<<\n");
                    animationPanel.setBlocked(true); // позначка блокування
                    
                    Thread.sleep(3000); // критична секція обчислень
                    
                    calculationArea.append(">>> РОЗБЛОКУВАННЯ <<<\n\n");
                    animationPanel.setBlocked(false);
                    condition.signalAll(); // розбудити анімацію
                } catch (InterruptedException ex) {
                    ex.printStackTrace();
                } finally {
                    sharedLock.unlock();
                }
            } else {
                JOptionPane.showMessageDialog(this,
                    "Запустіть спочатку обидва потоки!",
                    "Помилка", JOptionPane.WARNING_MESSAGE);
            }
        }).start();
    }
    
    // Потік 1: створення й запуск
    class AnimationThread extends Thread {
        private volatile boolean running = true;
        private volatile boolean paused = false;
        private volatile int speed = 50;
        
        @Override
        public void run() {
            while (running) {
                if (!paused) {
                    sharedLock.lock();
                    try {
                        while (animationPanel.isBlocked()) {
                            condition.await(); // чекає сигналу
                        }
                    } catch (InterruptedException e) {
                        break;
                    } finally {
                        sharedLock.unlock();
                    }
                    
                    animationPanel.update();
                    animationPanel.repaint();
                    
                    try {
                        Thread.sleep(50 - speed / 2);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }
        
        public void pauseThread() { paused = true; }
        public void resumeThread() { paused = false; }
        public void stopThread() { running = false; interrupt(); }
        public void setSpeed(int speed) { this.speed = speed; }
    }
    
    // Малювання зображення
    class AnimationPanel extends JPanel {
        private double angle = 0;
        private boolean blocked = false;
        
        public void update() {
            angle += 0.05;
        }
        
        public void reset() {
            angle = 0;
            blocked = false;
            repaint();
        }
        
        public boolean isBlocked() { return blocked; }
        public void setBlocked(boolean blocked) { this.blocked = blocked; }
        
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g;
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            
            int width = getWidth();
            int height = getHeight();
            int centerX = width / 2;
            int centerY = height / 2;
            
            for (int i = 0; i < 8; i++) {
                double currentAngle = angle + i * Math.PI / 4;
                int radius = 60;
                
                int x = centerX + (int)(radius * Math.cos(currentAngle));
                int y = centerY + (int)(radius * Math.sin(currentAngle));
                
                Color color = new Color(100 + i * 20, 150, 255 - i * 20);
                g2d.setColor(color);
                g2d.fillOval(x - 15, y - 15, 30, 30);
            }
            
            g2d.setColor(Color.BLUE);
            g2d.setStroke(new BasicStroke(2));
            
            for (int x = 0; x < width - 1; x++) {
                double t1 = (x - centerX) / 40.0 + angle;
                double t2 = (x + 1 - centerX) / 40.0 + angle;
                
                int y1 = centerY - (int)(40 * Math.sin(t1));
                int y2 = centerY - (int)(40 * Math.sin(t2));
                
                g2d.drawLine(x, y1, x + 1, y2);
            }
            
            if (blocked) {
                g2d.setColor(new Color(255, 0, 0, 100));
                g2d.fillRect(0, 0, width, height);
                g2d.setColor(Color.RED);
                g2d.setFont(new Font("Arial", Font.BOLD, 18));
                g2d.drawString("ЗАБЛОКОВАНО", 20, 30);
            }
        }
    }
    
    //Другий потік
    class CalculationThread extends Thread {
        private volatile boolean running = true;
        private volatile boolean paused = false;
        private volatile int delay = 500;
        private int count = 0;
        
        @Override
        public void run() {
            while (running) {
                if (!paused) {
                    performCalculation(); // обчислення
                    try {
                        Thread.sleep(delay);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }
        
        private void performCalculation() {
            count++;
            
            long fib = fibonacci(count % 25 + 10);
            long fact = factorial(count % 12 + 1);
            
            double sum = 0;
            for (int i = 1; i <= 50; i++) {
                sum += 1.0 / (i * i);
            }
            
            final int finalCount = count;
            final long finalFib = fib;
            final long finalFact = fact;
            final double finalSum = sum;
            
            SwingUtilities.invokeLater(() -> {
                calculationArea.append(String.format(
                    "Обчислення #%d\n" +
                    "Fibonacci(%d) = %d\n" +
                    "Factorial(%d) = %d\n" +
                    "Sum = %.4f\n" +
                    "Priority: %d\n\n",
                    finalCount,
                    finalCount % 25 + 10, finalFib,
                    finalCount % 12 + 1, finalFact,
                    finalSum,
                    Thread.currentThread().getPriority()
                ));
                calculationArea.setCaretPosition(calculationArea.getDocument().getLength());
            });
        }
        
        private long fibonacci(int n) {
            if (n <= 1) return n;
            long a = 0, b = 1;
            for (int i = 2; i <= n; i++) {
                long temp = a + b;
                a = b;
                b = temp;
            }
            return b;
        }
        
        private long factorial(int n) {
            long result = 1;
            for (int i = 2; i <= n; i++) {
                result *= i;
            }
            return result;
        }
        
        public void pauseThread() { paused = true; }
        public void resumeThread() { paused = false; }
        public void stopThread() { running = false; interrupt(); }
        public void setDelay(int delay) { this.delay = delay; }
    }
    
    // Третій потік
    class ScrollingThread extends Thread {
        private volatile boolean running = true;
        private volatile boolean paused = false;
        
        @Override
        public void run() {
            while (running) {
                if (!paused) {
                    scrollingPanel.scroll(); // зсув тексту
                    scrollingPanel.repaint(); // перемальовка
                    
                    try {
                        Thread.sleep(30);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }
        
        public void pauseThread() { paused = true; }
        public void resumeThread() { paused = false; }
        public void stopThread() { running = false; interrupt(); }
    }
    
    // Панель, що малює і рухає текст
    class ScrollingPanel extends JPanel {
        private String text = "Багатопоточне програмування в Java";
        private int xPosition = 0;
        private int speed = 5;
        
        public void scroll() {
            xPosition -= speed;
            FontMetrics fm = getFontMetrics(new Font("Arial", Font.BOLD, 20));
            int textWidth = fm.stringWidth(text);
            
            if (xPosition < -textWidth) {
                xPosition = getWidth();
            }
        }
        
        public void reset() {
            xPosition = getWidth();
            repaint();
        }
        
        public void setText(String text) {
            this.text = text;
            xPosition = getWidth();
        }
        
        public void setSpeed(int speed) {
            this.speed = speed;
        }
        
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2d = (Graphics2D) g;
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            
            g2d.setFont(new Font("Arial", Font.BOLD, 20));
            g2d.setColor(Color.BLUE);
            g2d.drawString(text, xPosition, getHeight() / 2);
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception e) {
                e.printStackTrace();
            }
            
            lab4 demo = new lab4();
            demo.setVisible(true);
        });
    }
}