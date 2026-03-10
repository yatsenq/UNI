import javax.swing.*;
import javax.swing.event.HyperlinkEvent;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.util.ArrayList;

//1. графічне застосування
public class SimpleBrowser extends JFrame {
    private JEditorPane editorPane;
    private JTextField urlField;
    private JLabel statusLabel;
    private ArrayList<String> favorites;
    private JCheckBox darkModeCheckBox;
    private JRadioButton homePageRadio, customPageRadio;
    private JList<String> historyList;
    private DefaultListModel<String> historyModel;
    private JTextField customPageField;
    private String customHomePage = "";
    private int currentFontSize = 14;
    
    private ArrayList<String> navigationHistory;
    private int currentHistoryIndex;
    private JButton backButton, forwardButton;
    
    private JPanel mainPanel, leftPanel, rightPanel, statusPanel;
    private JToolBar toolBar;

    public SimpleBrowser() {
        setTitle("Простий Web-Браузер");
        setSize(900, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        favorites = new ArrayList<>();
        historyModel = new DefaultListModel<>();
        navigationHistory = new ArrayList<>();
        currentHistoryIndex = -1;

        createMenuBar();
        createToolBar();
        createMainPanel();
        createStatusBar();
        setVisible(true);
    }

    private void createMenuBar() {
        JMenuBar menuBar = new JMenuBar();
        
        // меню
        JMenu fileMenu = new JMenu("Файл");
        JMenuItem openItem = new JMenuItem("Відкрити URL");
        JMenuItem saveItem = new JMenuItem("Зберегти сторінку");
        JMenuItem exitItem = new JMenuItem("Вихід");

        openItem.addActionListener(e -> openURL());
        saveItem.addActionListener(e -> savePage());
        exitItem.addActionListener(e -> System.exit(0));

        fileMenu.add(openItem);
        fileMenu.add(saveItem);
        fileMenu.addSeparator();
        fileMenu.add(exitItem);

        JMenu bookmarksMenu = new JMenu("Закладки");
        JMenuItem addBookmark = new JMenuItem("Додати в закладки");
        JMenuItem showBookmarks = new JMenuItem("Показати закладки");
        JMenuItem manageBookmarks = new JMenuItem("Керувати закладками");

        addBookmark.addActionListener(e -> addToFavorites());
        showBookmarks.addActionListener(e -> showFavorites());
        manageBookmarks.addActionListener(e -> manageFavorites());

        bookmarksMenu.add(addBookmark);
        bookmarksMenu.add(showBookmarks);
        bookmarksMenu.add(manageBookmarks);

        JMenu settingsMenu = new JMenu("Налаштування");
        JMenuItem preferences = new JMenuItem("Параметри");
        preferences.addActionListener(e -> showSettingsDialog());
        settingsMenu.add(preferences);

        JMenu helpMenu = new JMenu("Довідка");
        JMenuItem aboutItem = new JMenuItem("Про програму");
        aboutItem.addActionListener(e -> showAboutDialog());
        helpMenu.add(aboutItem);

        menuBar.add(fileMenu);
        menuBar.add(bookmarksMenu);
        menuBar.add(settingsMenu);
        menuBar.add(helpMenu);
        setJMenuBar(menuBar);
    }

    private void createToolBar() {
        toolBar = new JToolBar();
        toolBar.setFloatable(false);

        //кнопки навігації(панель інструментів)
        backButton = new JButton("◄ Назад");
        backButton.setEnabled(false);
        backButton.addActionListener(e -> navigateBack());

        forwardButton = new JButton("Вперед ►");
        forwardButton.setEnabled(false);
        forwardButton.addActionListener(e -> navigateForward());

        JButton refreshButton = new JButton("↻ Оновити");
        refreshButton.addActionListener(e -> loadPage(urlField.getText(), false));

        JButton homeButton = new JButton("⌂ Домівка");
        homeButton.addActionListener(e -> goToHomePage());

        toolBar.add(backButton);
        toolBar.add(forwardButton);
        toolBar.add(refreshButton);
        toolBar.add(homeButton);
        toolBar.addSeparator();

        urlField = new JTextField("https://www.google.com");
        urlField.addActionListener(e -> loadPage(urlField.getText(), true));
        toolBar.add(new JLabel(" URL: "));
        toolBar.add(urlField);

        JButton goButton = new JButton("Перейти");
        goButton.addActionListener(e -> loadPage(urlField.getText(), true));
        toolBar.add(goButton);

        add(toolBar, BorderLayout.NORTH); // менеджер розміщення
    }

    private void createMainPanel() {
        mainPanel = new JPanel(new BorderLayout(5, 5));

        leftPanel = new JPanel();
        leftPanel.setLayout(new BoxLayout(leftPanel, BoxLayout.Y_AXIS)); //менеджер розміщення
        leftPanel.setBorder(BorderFactory.createTitledBorder("Історія"));
        leftPanel.setPreferredSize(new Dimension(150, 0));

        historyList = new JList<>(historyModel); //список
        historyList.addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) {
                String selectedUrl = historyList.getSelectedValue();
                if (selectedUrl != null) {
                    urlField.setText(selectedUrl);
                    loadPage(selectedUrl, true);
                }
            }
        });
        JScrollPane historyScroll = new JScrollPane(historyList);
        leftPanel.add(historyScroll);

        editorPane = new JEditorPane();
        editorPane.setEditable(false);
        editorPane.setContentType("text/html");
        
        editorPane.addHyperlinkListener(e -> {
            if (e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
                loadPage(e.getURL().toString(), true);
            }
        });

        JPopupMenu popupMenu = new JPopupMenu(); // спливаюче меню
        JMenuItem copyItem = new JMenuItem("Копіювати");
        JMenuItem selectAllItem = new JMenuItem("Виділити все");
        JMenuItem addFavItem = new JMenuItem("Додати в закладки");

        copyItem.addActionListener(e -> editorPane.copy());
        selectAllItem.addActionListener(e -> editorPane.selectAll());
        addFavItem.addActionListener(e -> addToFavorites());

        popupMenu.add(copyItem);
        popupMenu.add(selectAllItem);
        popupMenu.addSeparator();
        popupMenu.add(addFavItem);

        // при пкм вилазить 
        editorPane.setComponentPopupMenu(popupMenu);

        JScrollPane scrollPane = new JScrollPane(editorPane);

        rightPanel = new JPanel();
        rightPanel.setLayout(new BoxLayout(rightPanel, BoxLayout.Y_AXIS)); //менеджер розміщення
        rightPanel.setBorder(BorderFactory.createTitledBorder("Опції"));
        rightPanel.setPreferredSize(new Dimension(150, 0));

        darkModeCheckBox = new JCheckBox("Темна тема", false); //прапорець
        darkModeCheckBox.addActionListener(e -> {
            toggleDarkMode(darkModeCheckBox.isSelected());
            statusLabel.setText("Тема: " + (darkModeCheckBox.isSelected() ? "Темна" : "Світла"));
        });

        ButtonGroup group = new ButtonGroup();
        homePageRadio = new JRadioButton("Google (за замовчуванням)", true); //перемикачі
        customPageRadio = new JRadioButton("Власна сторінка");
        group.add(homePageRadio);
        group.add(customPageRadio);
        
        customPageField = new JTextField();
        customPageField.setMaximumSize(new Dimension(140, 25));
        customPageField.setEnabled(false);
        
        customPageRadio.addActionListener(e -> {
            customPageField.setEnabled(true);
            showCustomPageDialog();
        });
        
        homePageRadio.addActionListener(e -> {
            customPageField.setEnabled(false);
            customHomePage = "";
        });

        rightPanel.add(darkModeCheckBox);
        rightPanel.add(Box.createVerticalStrut(15));
        rightPanel.add(new JLabel("Початкова сторінка:"));
        rightPanel.add(homePageRadio);
        rightPanel.add(customPageRadio);
        rightPanel.add(Box.createVerticalStrut(5));
        rightPanel.add(new JLabel("URL:"));
        rightPanel.add(customPageField);

        mainPanel.add(leftPanel, BorderLayout.WEST);
        mainPanel.add(scrollPane, BorderLayout.CENTER);
        mainPanel.add(rightPanel, BorderLayout.EAST);

        add(mainPanel, BorderLayout.CENTER);
    }

    private void createStatusBar() {
        statusPanel = new JPanel(new FlowLayout(FlowLayout.LEFT)); //менеджер розміщення
        statusLabel = new JLabel("Готовий"); //рядок стану
        statusPanel.add(statusLabel);
        add(statusPanel, BorderLayout.SOUTH);//менеджер розміщення
    }

    private void toggleDarkMode(boolean isDark) {
        if (isDark) {
            mainPanel.setBackground(new Color(45, 45, 45));
            leftPanel.setBackground(new Color(45, 45, 45));
            rightPanel.setBackground(new Color(45, 45, 45));
            statusPanel.setBackground(new Color(30, 30, 30));
            toolBar.setBackground(new Color(50, 50, 50));
            editorPane.setBackground(new Color(60, 60, 60));
            editorPane.setForeground(Color.WHITE);
            historyList.setBackground(new Color(60, 60, 60));
            historyList.setForeground(Color.WHITE);
            statusLabel.setForeground(Color.WHITE);
            
            for (Component comp : rightPanel.getComponents()) {
                comp.setForeground(Color.WHITE);
                if (comp instanceof JLabel || comp instanceof JCheckBox || comp instanceof JRadioButton) {
                    comp.setBackground(new Color(45, 45, 45));
                }
            }
        } else {
            mainPanel.setBackground(null);
            leftPanel.setBackground(null);
            rightPanel.setBackground(null);
            statusPanel.setBackground(null);
            toolBar.setBackground(null);
            editorPane.setBackground(Color.WHITE);
            editorPane.setForeground(Color.BLACK);
            historyList.setBackground(Color.WHITE);
            historyList.setForeground(Color.BLACK);
            statusLabel.setForeground(Color.BLACK);
            
            for (Component comp : rightPanel.getComponents()) {
                comp.setForeground(Color.BLACK);
                if (comp instanceof JLabel || comp instanceof JCheckBox || comp instanceof JRadioButton) {
                    comp.setBackground(null);
                }
            }
        }
        repaint();
    }

    private void changeFontSize(int size) {
        currentFontSize = size;
        
        String bodyRule = "body { font-family: " + editorPane.getFont().getFamily() + 
                        "; font-size: " + size + "pt; }";
        ((javax.swing.text.html.HTMLDocument) editorPane.getDocument())
            .getStyleSheet().addRule(bodyRule);
        
        String currentUrl = urlField.getText();
        if (!currentUrl.isEmpty()) {
            try {
                editorPane.setPage(currentUrl);
            } catch (IOException ex) {
            }
        }
    }

    private void showCustomPageDialog() {
        String url = JOptionPane.showInputDialog(this, 
            "Введіть URL власної початкової сторінки:", 
            "Власна сторінка", 
            JOptionPane.PLAIN_MESSAGE);
        
        if (url != null && !url.trim().isEmpty()) {
            customHomePage = url;
            customPageField.setText(url);
            statusLabel.setText("Власна сторінка встановлена: " + url);
        } else {
            homePageRadio.setSelected(true);
            customPageField.setEnabled(false);
            customPageField.setText("");
        }
    }

    private void goToHomePage() {
        if (customPageRadio.isSelected() && !customHomePage.isEmpty()) {
            urlField.setText(customHomePage);
            loadPage(customHomePage, true);
        } else {
            urlField.setText("https://www.google.com");
            loadPage("https://www.google.com", true);
        }
    }

    private void loadPage(String url, boolean addToHistory) {
        try {
            statusLabel.setText("Завантаження: " + url);
            editorPane.setPage(url);
            urlField.setText(url);
            
            if (!historyModel.contains(url)) {
                historyModel.addElement(url);
            }
            
            if (addToHistory) {
                while (navigationHistory.size() > currentHistoryIndex + 1) {
                    navigationHistory.remove(navigationHistory.size() - 1);
                }
                navigationHistory.add(url);
                currentHistoryIndex = navigationHistory.size() - 1;
                updateNavigationButtons();
            }
            
            statusLabel.setText("Завантажено: " + url);
        } catch (IOException e) {
            statusLabel.setText("Помилка завантаження");
            JOptionPane.showMessageDialog(this, 
                "Не вдалося завантажити сторінку:\n" + e.getMessage(),
                "Помилка", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void navigateBack() {
        if (currentHistoryIndex > 0) {
            currentHistoryIndex--;
            String url = navigationHistory.get(currentHistoryIndex);
            urlField.setText(url);
            loadPage(url, false);
            updateNavigationButtons();
            statusLabel.setText("Назад: " + url);
        }
    }

    private void navigateForward() {
        if (currentHistoryIndex < navigationHistory.size() - 1) {
            currentHistoryIndex++;
            String url = navigationHistory.get(currentHistoryIndex);
            urlField.setText(url);
            loadPage(url, false);
            updateNavigationButtons();
            statusLabel.setText("Вперед: " + url);
        }
    }

    private void updateNavigationButtons() {
        backButton.setEnabled(currentHistoryIndex > 0);
        forwardButton.setEnabled(currentHistoryIndex < navigationHistory.size() - 1);
    }

    private void openURL() {
        String url = JOptionPane.showInputDialog(this, "Введіть URL:",  // діалогові вікна(стандартне)
            "Відкрити URL", JOptionPane.PLAIN_MESSAGE);
        if (url != null && !url.trim().isEmpty()) {
            loadPage(url, true);
        }
    }

    private void savePage() {
        JFileChooser fileChooser = new JFileChooser(); // діалогові вікна(стандартне)
        fileChooser.setDialogTitle("Зберегти сторінку");
        int result = fileChooser.showSaveDialog(this);
        
        if (result == JFileChooser.APPROVE_OPTION) {
            try {
                File file = fileChooser.getSelectedFile();
                FileWriter writer = new FileWriter(file);
                writer.write(editorPane.getText());
                writer.close();
                statusLabel.setText("Збережено: " + file.getName());
                JOptionPane.showMessageDialog(this, "Сторінку збережено успішно!");
            } catch (IOException e) {
                JOptionPane.showMessageDialog(this, 
                    "Помилка збереження: " + e.getMessage(),
                    "Помилка", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void addToFavorites() {
        String currentUrl = urlField.getText();
        if (!currentUrl.isEmpty() && !favorites.contains(currentUrl)) {
            favorites.add(currentUrl);
            statusLabel.setText("Додано в закладки: " + currentUrl);
            JOptionPane.showMessageDialog(this, "Сторінку додано в закладки!"); // діалогові вікна(стандартне)
        } else if (favorites.contains(currentUrl)) {
            JOptionPane.showMessageDialog(this, "Ця сторінка вже є в закладках!");
        }
    }

    private void showFavorites() {
        if (favorites.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Закладки порожні");
            return;
        }
        
        String[] favArray = favorites.toArray(new String[0]); //діалогові вікна(стандартне)
        String selected = (String) JOptionPane.showInputDialog(this,
            "Виберіть закладку:", "Закладки",
            JOptionPane.PLAIN_MESSAGE, null, favArray, favArray[0]);
        
        if (selected != null) {
            loadPage(selected, true);
        }
    }

    private void manageFavorites() {
        if (favorites.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Закладки порожні");
            return;
        }

        JDialog manageDialog = new JDialog(this, "Керування закладками", true);//діалогові вікна(власні)
        manageDialog.setSize(500, 400);
        manageDialog.setLocationRelativeTo(this);
        manageDialog.setLayout(new BorderLayout(10, 10));

        DefaultListModel<String> favModel = new DefaultListModel<>(); //список
        for (String fav : favorites) {
            favModel.addElement(fav);
        }

        JList<String> favList = new JList<>(favModel);
        favList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        JScrollPane scrollPane = new JScrollPane(favList);

        JPanel buttonPanel = new JPanel(new FlowLayout());
        
        JButton openButton = new JButton("Відкрити");
        openButton.addActionListener(e -> {
            String selected = favList.getSelectedValue();
            if (selected != null) {
                loadPage(selected, true);
                manageDialog.dispose();
            } else {
                JOptionPane.showMessageDialog(manageDialog, "Виберіть закладку!");
            }
        });

        JButton deleteButton = new JButton("Видалити");
        deleteButton.addActionListener(e -> {
            int selectedIndex = favList.getSelectedIndex();
            if (selectedIndex != -1) {
                String removed = favModel.remove(selectedIndex);
                favorites.remove(removed);
                statusLabel.setText("Видалено закладку: " + removed);
                JOptionPane.showMessageDialog(manageDialog, "Закладку видалено!");
                
                if (favModel.isEmpty()) {
                    manageDialog.dispose();
                }
            } else {
                JOptionPane.showMessageDialog(manageDialog, "Виберіть закладку для видалення!");
            }
        });

        JButton closeButton = new JButton("Закрити");
        closeButton.addActionListener(e -> manageDialog.dispose());

        buttonPanel.add(openButton);
        buttonPanel.add(deleteButton);
        buttonPanel.add(closeButton);

        manageDialog.add(new JLabel("  Закладки:"), BorderLayout.NORTH);
        manageDialog.add(scrollPane, BorderLayout.CENTER);
        manageDialog.add(buttonPanel, BorderLayout.SOUTH);
        manageDialog.setVisible(true);
    }

    private void showSettingsDialog() {
        JDialog settingsDialog = new JDialog(this, "Налаштування", true);//діалогові вікна(власні налаштування)
        settingsDialog.setSize(400, 300);
        settingsDialog.setLocationRelativeTo(this);
        settingsDialog.setLayout(new BorderLayout(10, 10));

        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(4, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        panel.add(new JLabel("Домашня сторінка:"));
        JTextField homePageField = new JTextField("https://www.google.com");
        panel.add(homePageField);

        panel.add(new JLabel("Розмір шрифту:"));
        JComboBox<String> fontSizeCombo = new JComboBox<>(new String[]{"Малий", "Середній", "Великий"});
        fontSizeCombo.setSelectedIndex(1); 
        
        fontSizeCombo.addActionListener(e -> {
            String selected = (String) fontSizeCombo.getSelectedItem();
            int size = 14;
            
            if ("Малий".equals(selected)) {
                size = 12;
            } else if ("Середній".equals(selected)) {
                size = 14;
            } else if ("Великий".equals(selected)) {
                size = 18;
            }
            
            changeFontSize(size);
            statusLabel.setText("Розмір шрифту змінено: " + selected + " (" + size + "pt)");
        });
        
        panel.add(fontSizeCombo);

        panel.add(new JLabel("Очистити історію:"));
        JButton clearHistoryBtn = new JButton("Очистити");
        clearHistoryBtn.addActionListener(e -> {
            historyModel.clear();
            navigationHistory.clear();
            currentHistoryIndex = -1;
            updateNavigationButtons();
            JOptionPane.showMessageDialog(settingsDialog, "Історію очищено!");
        });
        panel.add(clearHistoryBtn);

        panel.add(new JLabel("Очистити закладки:"));
        JButton clearFavBtn = new JButton("Очистити");
        clearFavBtn.addActionListener(e -> {
            favorites.clear();
            JOptionPane.showMessageDialog(settingsDialog, "Закладки очищено!");
        });
        panel.add(clearFavBtn);

        JButton okButton = new JButton("OK");
        okButton.addActionListener(e -> settingsDialog.dispose());

        settingsDialog.add(panel, BorderLayout.CENTER);
        settingsDialog.add(okButton, BorderLayout.SOUTH);
        settingsDialog.setVisible(true);
    }

    private void showAboutDialog() {
        JOptionPane.showMessageDialog(this,
            "Простий Web-Браузер \n\n" +
            "Функції:\n" +
            "1. Навігація (Назад/Вперед)\n" +
            "2. Закладки з можливістю видалення\n" +
            "3. Темна/Світла тема\n" +
            "4. Власна початкова сторінка\n" +
            "5. Історія перегляду\n" +
            "6. Збереження сторінок\n" +
            "7. Зміна розміру шрифту\n\n" +
            "Демонстрація GUI на Java Swing",
            "Про програму", JOptionPane.INFORMATION_MESSAGE);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SimpleBrowser());
    }
}

//http://example.com
//http://info.cern.ch
//file:///C:/Users/igrew/OneDrive/Desktop/UNI/Java/LAB3/test.html



