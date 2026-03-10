package com.lab5.dbapp;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Graphics2D;
import java.awt.GridLayout;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.JTree;
import javax.swing.SwingUtilities;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreeNode;

public class MainWindow extends JFrame {

    private final DatabaseManager db = new DatabaseManager();

    private JTree tree;
    private JTable table;

    private TableDataModel currentModel;
    private String currentTable;

    private JPopupMenu tablePopup;

    public MainWindow() {
        setTitle("Lab 5 – DB Browser (SQLite)");
        setSize(1000, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        setJMenuBar(createMenuBar());

        tree = new JTree();
        tree.setModel(new DefaultTreeModel(new DefaultMutableTreeNode("No database")));
        tree.setCellRenderer(new DbTreeCellRenderer());

        table = new JTable();

        JScrollPane treeScroll = new JScrollPane(tree);
        JScrollPane tableScroll = new JScrollPane(table);

        JSplitPane split = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, treeScroll, tableScroll);
        split.setDividerLocation(300);
        add(split, BorderLayout.CENTER);

        initTreeSelection();
        initPopupMenu();
    }

    // ------------ MENU -------------

    private void openSqlDialog() {
    JTextArea textArea = new JTextArea(10, 40);
    JScrollPane scroll = new JScrollPane(textArea);

    int result = JOptionPane.showConfirmDialog(
            this,
            scroll,
            "Введіть SQL запит",
            JOptionPane.OK_CANCEL_OPTION,
            JOptionPane.PLAIN_MESSAGE
    );

    if (result == JOptionPane.OK_OPTION) {
        String sql = textArea.getText().trim();
        if (!sql.isEmpty()) {
            executeUserQuery(sql);}
        }
    }


    private JMenuBar createMenuBar() {
        JMenuBar mb = new JMenuBar();

        JMenu mDb = new JMenu("Database");

        JMenuItem miConnect = new JMenuItem("Connect");
        miConnect.addActionListener(e -> onConnect());
        JMenuItem miDisconnect = new JMenuItem("Disconnect");
        miDisconnect.addActionListener(e -> onDisconnect());
        JMenuItem miExit = new JMenuItem("Exit");
        miExit.addActionListener(e -> System.exit(0));

        JMenuItem runQueryItem = new JMenuItem("Run SQL...");
        runQueryItem.addActionListener(e -> openSqlDialog());
        mDb.add(runQueryItem);

        mDb.add(miConnect);
        mDb.add(miDisconnect);
        mDb.addSeparator();
        mDb.add(miExit);

        JMenu mTable = new JMenu("Table");
        JMenuItem miInsert = new JMenuItem("Insert");
        miInsert.addActionListener(e -> onInsert());
        JMenuItem miEdit = new JMenuItem("Edit");
        miEdit.addActionListener(e -> onEdit());
        JMenuItem miDelete = new JMenuItem("Delete");
        miDelete.addActionListener(e -> onDelete());

        mTable.add(miInsert);
        mTable.add(miEdit);
        mTable.add(miDelete);

        JMenu mSearch = new JMenu("Search");
        JMenuItem miSearch = new JMenuItem("Search in table...");
        miSearch.addActionListener(e -> onSearch());
        mSearch.add(miSearch);

        JMenu mHelp = new JMenu("Help");
        JMenuItem miDbMeta = new JMenuItem("DatabaseMetadata");
        miDbMeta.addActionListener(e -> showDbMetadata());
        JMenuItem miRsMeta = new JMenuItem("ResultSetMetadata");
        miRsMeta.addActionListener(e -> showResultSetMetadata());
        JMenuItem miAbout = new JMenuItem("About");
        miAbout.addActionListener(e -> showAbout());
        mHelp.add(miDbMeta);
        mHelp.add(miRsMeta);
        mHelp.addSeparator();
        mHelp.add(miAbout);

        mb.add(mDb);
        mb.add(mTable);
        mb.add(mSearch);
        mb.add(mHelp);

        return mb;
    }

    // ------------ CONNECT / DISCONNECT -------------

    private void onConnect() {
        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle("Select SQLite database file");
        if (chooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            String path = chooser.getSelectedFile().getAbsolutePath();
            if (db.connect(path)) {
                loadDatabaseStructure();
                setTitle("Lab 5 – " + path);
            } else {
                JOptionPane.showMessageDialog(this, "Cannot connect to DB",
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void onDisconnect() {
        db.disconnect();
        currentModel = null;
        currentTable = null;
        table.setModel(new DefaultTableModel());
        tree.setModel(new DefaultTreeModel(new DefaultMutableTreeNode("No database")));
        setTitle("Lab 5 – DB Browser");
    }

    // ------------ TREE STRUCTURE -------------
    private void loadDatabaseStructure() {
        try {
            DefaultMutableTreeNode root =
                    new DefaultMutableTreeNode("Database: " + db.getDbPath());

            DefaultMutableTreeNode tablesNode = new DefaultMutableTreeNode("Tables");
            for (String t : db.getTables()) {
                tablesNode.add(new DefaultMutableTreeNode(t));
            }
            root.add(tablesNode);

            DefaultMutableTreeNode viewsNode = new DefaultMutableTreeNode("Views");
            for (String v : db.getViews()) {
                viewsNode.add(new DefaultMutableTreeNode(v));
            }
            root.add(viewsNode);

            DefaultMutableTreeNode trigNode = new DefaultMutableTreeNode("Triggers");
            for (String tr : db.getTriggers()) {
                trigNode.add(new DefaultMutableTreeNode(tr));
            }
            root.add(trigNode);

            tree.setModel(new DefaultTreeModel(root));
            expandAll(tree);

        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this, "Error reading DB structure: " + e.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void expandAll(JTree tree) {
        for (int i = 0; i < tree.getRowCount(); i++) {
            tree.expandRow(i);
        }
    }

    private void initTreeSelection() {
        tree.addTreeSelectionListener(new TreeSelectionListener() {
            @Override
            public void valueChanged(TreeSelectionEvent e) {
                DefaultMutableTreeNode node =
                        (DefaultMutableTreeNode) tree.getLastSelectedPathComponent();
                if (node == null || !db.isConnected()) return;

                DefaultMutableTreeNode parent =
                        (DefaultMutableTreeNode) node.getParent();
                if (parent == null) return;

                Object parentObj = parent.getUserObject();
                if ("Tables".equals(parentObj)) {
                    String tableName = node.getUserObject().toString();
                    loadTable(tableName);
                }
            }
        });
    }

    private void loadTable(String tableName) {
        try {
            currentTable = tableName;
    currentModel = db.loadTableData(tableName);
    table.setModel(currentModel);
    } catch (Exception e) {
        e.printStackTrace();
        JOptionPane.showMessageDialog(this, "Error loading table: " + e.getMessage(),
                "Error", JOptionPane.ERROR_MESSAGE);
}
    }

    // ------------ POPUP MENU ON TREE -------------
    private void initPopupMenu() {
        tablePopup = new JPopupMenu();
        JMenuItem miInsert = new JMenuItem("Insert");
        miInsert.addActionListener(e -> onInsert());
        JMenuItem miEdit = new JMenuItem("Edit");
        miEdit.addActionListener(e -> onEdit());
        JMenuItem miDelete = new JMenuItem("Delete");
        miDelete.addActionListener(e -> onDelete());
        JMenuItem miSearch = new JMenuItem("Search");
        miSearch.addActionListener(e -> onSearch());

        tablePopup.add(miInsert);
        tablePopup.add(miEdit);
        tablePopup.add(miDelete);
        tablePopup.addSeparator();
        tablePopup.add(miSearch);

        tree.addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                showIfPopup(e);
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                showIfPopup(e);
            }

            private void showIfPopup(MouseEvent e) {
                if (e.isPopupTrigger()) {
                    int row = tree.getRowForLocation(e.getX(), e.getY());
                    if (row == -1) return;
                    tree.setSelectionRow(row);
                    DefaultMutableTreeNode node =
                            (DefaultMutableTreeNode) tree.getLastSelectedPathComponent();
                    if (node == null) return;
                    DefaultMutableTreeNode parent =
                            (DefaultMutableTreeNode) node.getParent();
                    if (parent != null && "Tables".equals(parent.getUserObject())) {
                        String tableName = node.getUserObject().toString();
                        loadTable(tableName);
                        tablePopup.show(tree, e.getX(), e.getY());
                    }
                }
            }
        });
    }

    // ------------ TABLE OPERATIONS -------------
    private void onInsert() {
        if (!checkTableSelected()) return;
        try {
            List<ColumnInfo> cols = db.getTableColumns(currentTable);
            List<Object> values = showRowEditDialog(cols, null);
            if (values == null) return; 
            db.insertRow(currentTable, cols, values);
            loadTable(currentTable);
        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Insert error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void onEdit() {
        if (!checkTableSelected()) return;
        int row = table.getSelectedRow();
        if (row == -1) {
            JOptionPane.showMessageDialog(this, "Select a row to edit");
            return;
        }
        try {
            List<ColumnInfo> cols = db.getTableColumns(currentTable);
            List<Object> oldValues = currentModel.getRow(row);
            Object pkValue = currentModel.getValueAtRowPk(row);

            List<Object> newValues = showRowEditDialog(cols, oldValues);
            if (newValues == null) return;

            db.updateRow(currentTable, cols, newValues, pkValue);
            loadTable(currentTable);
        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Edit error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void onDelete() {
        if (!checkTableSelected()) return;
        int row = table.getSelectedRow();
        if (row == -1) {
            JOptionPane.showMessageDialog(this, "Select a row to delete");
            return;
        }
        int confirm = JOptionPane.showConfirmDialog(this,
                "Delete selected row?", "Confirm",
                JOptionPane.YES_NO_OPTION);
        if (confirm != JOptionPane.YES_OPTION) return;

        try {
            List<ColumnInfo> cols = db.getTableColumns(currentTable);
            Object pkValue = currentModel.getValueAtRowPk(row);
            db.deleteRow(currentTable, cols, pkValue);
            loadTable(currentTable);
        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Delete error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void onSearch() {
        if (!checkTableSelected()) return;
        try {
            List<ColumnInfo> cols = db.getTableColumns(currentTable);
            String[] colNames = cols.stream().map(ColumnInfo::name).toArray(String[]::new);

            JComboBox<String> combo = new JComboBox<>(colNames);
            JTextField tf = new JTextField();

            JPanel panel = new JPanel(new GridLayout(2, 2, 5, 5));
            panel.add(new JLabel("Column:"));
            panel.add(combo);
            panel.add(new JLabel("Contains:"));
            panel.add(tf);

            int res = JOptionPane.showConfirmDialog(this, panel,
                    "Search in " + currentTable,
                    JOptionPane.OK_CANCEL_OPTION);
            if (res != JOptionPane.OK_OPTION) return;

            String col = (String) combo.getSelectedItem();
            String pattern = tf.getText();

            TableDataModel model = db.search(currentTable, cols, col, pattern);
            table.setModel(model);
            currentModel = model;

        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Search error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private boolean checkTableSelected() {
        if (!db.isConnected()) {
            JOptionPane.showMessageDialog(this, "No DB connection");
            return false;
        }
        if (currentTable == null) {
            JOptionPane.showMessageDialog(this, "Select a table first");
            return false;
        }
        return true;
    }

    private List<Object> showRowEditDialog(List<ColumnInfo> cols, List<Object> oldValues) {
        List<JTextField> fields = new ArrayList<>();
        JPanel panel = new JPanel(new GridLayout(cols.size(), 2, 5, 5));

        for (int i = 0; i < cols.size(); i++) {
            ColumnInfo c = cols.get(i);
            JTextField tf = new JTextField();
            if (oldValues != null && oldValues.size() > i && oldValues.get(i) != null) {
                tf.setText(String.valueOf(oldValues.get(i)));
            }
            if (c.isPk()) {
                tf.setEditable(false);
                tf.setBackground(new Color(230, 230, 230));
            }
            panel.add(new JLabel(c.name() + (c.isPk() ? " [PK]" : "")));
            panel.add(tf);
            fields.add(tf);
        }

        int res = JOptionPane.showConfirmDialog(this, panel,
                (oldValues == null ? "Insert into " : "Edit ") + currentTable,
                JOptionPane.OK_CANCEL_OPTION);
        if (res != JOptionPane.OK_OPTION) return null;

        List<Object> values = new ArrayList<>();
        for (int i = 0; i < cols.size(); i++) {
            ColumnInfo c = cols.get(i);
            String text = fields.get(i).getText();
            if (text.isEmpty()) {
                values.add(null);
            } else {
                values.add(text);
            }
        }
        return values;
    }

    // ------------ HELP -------------
    private void showDbMetadata() {
        if (!db.isConnected()) {
            JOptionPane.showMessageDialog(this, "No DB connection");
            return;
        }
        try {
            DatabaseMetaData md = db.getConnection().getMetaData();
            StringBuilder sb = new StringBuilder();
            sb.append("Database product: ").append(md.getDatabaseProductName()).append("\n");
            sb.append("Database version: ").append(md.getDatabaseProductVersion()).append("\n");
            sb.append("Driver: ").append(md.getDriverName()).append(" ").append(md.getDriverVersion()).append("\n");
            sb.append("URL: ").append(md.getURL()).append("\n");
            sb.append("User: ").append(md.getUserName()).append("\n");

            JTextArea area = new JTextArea(sb.toString(), 10, 50);
            area.setEditable(false);
            JOptionPane.showMessageDialog(this, new JScrollPane(area),
                    "DatabaseMetadata", JOptionPane.INFORMATION_MESSAGE);

        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private void showResultSetMetadata() {
        if (currentModel == null || currentTable == null) {
            JOptionPane.showMessageDialog(this, "Load a table first");
            return;
        }
        StringBuilder sb = new StringBuilder();
        sb.append("Table: ").append(currentTable).append("\n\n");
        List<ColumnInfo> cols = currentModel.getColumnsMeta();
        for (int i = 0; i < cols.size(); i++) {
            ColumnInfo c = cols.get(i);
            sb.append((i + 1)).append(". ")
                    .append(c.name())
                    .append("  (").append(c.type()).append(")")
                    .append(c.isPk() ? " [PK]" : "")
                    .append("\n");
        }
        JTextArea area = new JTextArea(sb.toString(), 10, 40);
        area.setEditable(false);
        JOptionPane.showMessageDialog(this, new JScrollPane(area),
                "ResultSetMetadata (by table info)", JOptionPane.INFORMATION_MESSAGE);
    }

    private void showAbout() {
        JLabel label = new JLabel(
                "<html><h2>Lab 5 – DB Browser</h2>" +
                        "<p>Author: <b>Vladyslav</b></p>" +
                        "<p>Site: <a href='https://example.com'>https://example.com</a></p>" +
                        "<p>Email: <a href='mailto:v4@gmail.com'>v4@gmail.com</a></p>" +
                        "</html>"
        );
        JOptionPane.showMessageDialog(this, label, "About", JOptionPane.INFORMATION_MESSAGE);
    }

    // ------------ TREE CELL RENDERER (власні іконки) -------------
    private static class DbTreeCellRenderer extends DefaultTreeCellRenderer {

        private final Icon dbIcon;
        private final Icon categoryIcon;
        private final Icon tableIcon;
        private final Icon viewIcon;
        private final Icon triggerIcon;

        public DbTreeCellRenderer() {
            dbIcon = createColorIcon(new Color(70, 130, 180));
            categoryIcon = createColorIcon(new Color(100, 100, 100));
            tableIcon = createColorIcon(new Color(46, 139, 87));
            viewIcon = createColorIcon(new Color(255, 140, 0));
            triggerIcon = createColorIcon(new Color(178, 34, 34));
        }

        @Override
        public Component getTreeCellRendererComponent(JTree tree, Object value,
                                                      boolean sel, boolean expanded,
                                                      boolean leaf, int row, boolean hasFocus) {
            Component c = super.getTreeCellRendererComponent(tree, value, sel, expanded, leaf, row, hasFocus);

            DefaultMutableTreeNode node = (DefaultMutableTreeNode) value;
            Object obj = node.getUserObject();

            if (row == 0) { 
                setIcon(dbIcon);
            } else {
                TreeNode parent = node.getParent();
                if (parent != null) {
                    Object parentObj = ((DefaultMutableTreeNode) parent).getUserObject();
                    if ("Tables".equals(parentObj)) {
                        if (leaf) setIcon(tableIcon);
                        else setIcon(categoryIcon);
                    } else if ("Views".equals(parentObj)) {
                        if (leaf) setIcon(viewIcon);
                        else setIcon(categoryIcon);
                    } else if ("Triggers".equals(parentObj)) {
                        if (leaf) setIcon(triggerIcon);
                        else setIcon(categoryIcon);
                    } else if ("Tables".equals(obj) || "Views".equals(obj) || "Triggers".equals(obj)) {
                        setIcon(categoryIcon);
                    }
                }
            }
            return c;
        }

        private static Icon createColorIcon(Color color) {
            int size = 12;
            BufferedImage img = new BufferedImage(size, size, BufferedImage.TYPE_INT_ARGB);
            Graphics2D g = img.createGraphics();
            g.setColor(color);
            g.fillRoundRect(0, 0, size - 1, size - 1, 4, 4);
            g.setColor(Color.DARK_GRAY);
            g.drawRoundRect(0, 0, size - 1, size - 1, 4, 4);
            g.dispose();
            return new ImageIcon(img);
        }
    }


    private void executeUserQuery(String sql) {
        if (!db.isConnected()) {
        JOptionPane.showMessageDialog(
                this,
                "Спочатку під’єднай базу даних (Database → Connect)!",
                "Немає з'єднання",
                JOptionPane.ERROR_MESSAGE
        );
        return;
    }

    try {
        Connection conn = db.getConnection();
        Statement stmt = conn.createStatement();

        if (sql.toLowerCase().startsWith("select") || sql.toLowerCase().startsWith("pragma")) {
            ResultSet rs = stmt.executeQuery(sql);
            TableDataModel model = new TableDataModel(rs);
            table.setModel(model);
            System.out.println("Запит виконано (SELECT)");
        } else {
            int rows = stmt.executeUpdate(sql);
            System.out.println("Успішно! Змінено рядків: " + rows);
        }

    } catch (Exception ex) {
        JOptionPane.showMessageDialog(
                this,
                "SQL помилка:\n" + ex.getMessage(),
                "Помилка",
                JOptionPane.ERROR_MESSAGE
        );
    }
    }

    // ------------ MAIN -------------

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new MainWindow().setVisible(true));
    }
}
