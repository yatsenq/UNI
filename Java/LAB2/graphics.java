import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import java.util.Random;

public class PolarFunctionGraph extends JPanel {
    private static final double A = 1.0;
    private static final double M = 0.5;
    
    private Color graphColor = Color.BLUE;
    private float lineWidth = 2.0f;
    private int lineStyle = 0;
    private Random random = new Random();
    
    public PolarFunctionGraph() {
        setBackground(Color.WHITE);
        
        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                changeGraphStyle();
                repaint();
            }
        });
    }
    
    private void changeGraphStyle() {
        graphColor = new Color(
            random.nextInt(256),
            random.nextInt(256),
            random.nextInt(256)
        );
        
        lineWidth = 1.0f + random.nextInt(5);
        
        lineStyle = random.nextInt(3);
    }
    
    private double calculateR(double phi) {
        return Math.pow(A, M) * Math.cos(M * phi);
    }
    
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, 
                            RenderingHints.VALUE_ANTIALIAS_ON);
        
        int width = getWidth();
        int height = getHeight();
        int centerX = width / 2;
        int centerY = height / 2;
        
        int scale = Math.min(width, height) / 4;
        
        g2d.setColor(Color.BLACK);
        g2d.setFont(new Font("Arial", Font.BOLD, 14));
        g2d.drawString("Яценко", 10, 20);
        g2d.drawString("Варіант № 30", 10, 40);
        
        g2d.setColor(Color.BLACK);
        g2d.setStroke(new BasicStroke(1.5f));
        
        g2d.drawLine(0, centerY, width, centerY);
        g2d.drawLine(centerX, 0, centerX, height);
        
        drawArrow(g2d, width - 10, centerY, width, centerY);
        drawArrow(g2d, centerX, 10, centerX, 0);
        
        g2d.setFont(new Font("Arial", Font.PLAIN, 12));
        g2d.drawString("x", width - 20, centerY - 10);
        g2d.drawString("y", centerX + 10, 15);
        
        g2d.setColor(new Color(220, 220, 220));
        g2d.setStroke(new BasicStroke(0.5f));
        for (int i = 1; i <= 3; i++) {
            int offset = i * scale;
            g2d.drawOval(centerX - offset, centerY - offset, 
                        2 * offset, 2 * offset);
        }
        
        g2d.setColor(graphColor);
        Stroke graphStroke;
        
        switch (lineStyle) {
            case 1: 
                graphStroke = new BasicStroke(
                    lineWidth,
                    BasicStroke.CAP_ROUND,
                    BasicStroke.JOIN_ROUND,
                    10.0f,
                    new float[]{10.0f, 10.0f},
                    0.0f
                );
                break;
            case 2:
                graphStroke = new BasicStroke(
                    lineWidth,
                    BasicStroke.CAP_ROUND,
                    BasicStroke.JOIN_ROUND,
                    10.0f,
                    new float[]{15.0f, 5.0f, 5.0f, 5.0f},
                    0.0f
                );
                break;
            default:
                graphStroke = new BasicStroke(lineWidth);
                break;
        }
        
        g2d.setStroke(graphStroke);
        
        g2d.setStroke(graphStroke);
        
        double step = 0.01;
        
        for (int branch = 0; branch < 2; branch++) {
            Path2D.Double path = new Path2D.Double();
            boolean firstPoint = true;
            
            for (double phi = 0; phi <= 4 * Math.PI; phi += step) {
                double cosValue = Math.cos(M * phi);
                double r = Math.pow(A, M) * cosValue;
                
                double actualR = (branch == 0) ? r : -r;
                double actualPhi = (branch == 0) ? phi : phi + Math.PI;
                
                if (actualR < 0) continue;
                
                double x = actualR * Math.cos(actualPhi);
                double y = actualR * Math.sin(actualPhi);
                
                int screenX = centerX + (int)(x * scale);
                int screenY = centerY - (int)(y * scale);
                
                if (firstPoint) {
                    path.moveTo(screenX, screenY);
                    firstPoint = false;
                } else {
                    path.lineTo(screenX, screenY);
                }
            }
            
            g2d.draw(path);
        }
        
        g2d.setColor(Color.BLACK);
        g2d.setFont(new Font("Arial", Font.PLAIN, 12));
        String formula = "r = a^m * cos(m*φ)";
        String params = "m = 1/2, a = 1";
        g2d.drawString(formula, 10, height - 35);
        g2d.drawString(params, 10, height - 20);
    }
    
    private void drawArrow(Graphics2D g2d, int x1, int y1, int x2, int y2) {
        int arrowSize = 8;
        double angle = Math.atan2(y2 - y1, x2 - x1);
        
        int[] xPoints = {
            x2,
            x2 - (int)(arrowSize * Math.cos(angle - Math.PI / 6)),
            x2 - (int)(arrowSize * Math.cos(angle + Math.PI / 6))
        };
        int[] yPoints = {
            y2,
            y2 - (int)(arrowSize * Math.sin(angle - Math.PI / 6)),
            y2 - (int)(arrowSize * Math.sin(angle + Math.PI / 6))
        };
        
        g2d.fillPolygon(xPoints, yPoints, 3);
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Графік полярної функції - Яценко, варіант 30");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.add(new PolarFunctionGraph());
            frame.setSize(800, 600);
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}