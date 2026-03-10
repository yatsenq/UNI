package com.lab5.dbapp;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class DatabaseManager {

    private Connection connection;
    private String dbPath;

    public boolean connect(String path) {
        try {
            disconnect();
            connection = DriverManager.getConnection("jdbc:sqlite:" + path);
            dbPath = path;
            System.out.println("Connected to: " + path);
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            connection = null;
            dbPath = null;
            return false;
        }
    }

    public void disconnect() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
                System.out.println("Disconnected");
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            connection = null;
            dbPath = null;
        }
    }

    public boolean isConnected() {
        try {
            return connection != null && !connection.isClosed();
        } catch (SQLException e) {
            return false;
        }
    }

    public Connection getConnection() {
        return connection;
    }

    public String getDbPath() {
        return dbPath;
    }

    // ========== STRUCTURE LOADERS ==========

    public List<String> getTables() throws SQLException {
        List<String> tables = new ArrayList<>();
        ResultSet rs = connection.getMetaData().getTables(null, null, "%", new String[]{"TABLE"});
        while (rs.next()) {
            String name = rs.getString("TABLE_NAME");
            if (!name.startsWith("sqlite_")) {
                tables.add(name);
            }
        }
        rs.close();
        return tables;
    }

    public List<String> getViews() throws SQLException {
        List<String> views = new ArrayList<>();
        ResultSet rs = connection.getMetaData().getTables(null, null, "%", new String[]{"VIEW"});
        while (rs.next()) {
            views.add(rs.getString("TABLE_NAME"));
        }
        rs.close();
        return views;
    }

    public List<String> getTriggers() throws SQLException {
        List<String> triggers = new ArrayList<>();
        String sql = "SELECT name FROM sqlite_master WHERE type='trigger'";
        try (Statement st = connection.createStatement();
             ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                triggers.add(rs.getString("name"));
            }
        }
        return triggers;
    }

    public List<ColumnInfo> getTableColumns(String table) throws SQLException {
        List<ColumnInfo> cols = new ArrayList<>();
        String pragma = "PRAGMA table_info('" + table + "')";
        try (Statement st = connection.createStatement();
             ResultSet rs = st.executeQuery(pragma)) {

            while (rs.next()) {
                cols.add(new ColumnInfo(
                        rs.getString("name"),
                        rs.getString("type"),
                        rs.getInt("pk") == 1
                ));
            }
        }
        return cols;
    }


    public TableDataModel loadTableData(String tableName) throws Exception {
    String sql = "SELECT * FROM \"" + tableName + "\"";

    Statement st = connection.createStatement();
    ResultSet rs = st.executeQuery(sql);

    return new TableDataModel(rs);
}


    // ========== CRUD ==========

    public void insertRow(String table, List<ColumnInfo> cols, List<Object> values) throws SQLException {
        StringBuilder sbCols = new StringBuilder();
        StringBuilder sbQ = new StringBuilder();
        List<Object> realValues = new ArrayList<>();

        for (int i = 0; i < cols.size(); i++) {
            ColumnInfo col = cols.get(i);
            if (col.isPk()) continue;

            if (sbCols.length() > 0) {
                sbCols.append(", ");
                sbQ.append(", ");
            }
            sbCols.append("\"").append(col.name()).append("\"");
            sbQ.append("?");
            realValues.add(values.get(i));
        }

        String sql = "INSERT INTO \"" + table + "\"(" + sbCols + ") VALUES(" + sbQ + ")";
        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            for (int i = 0; i < realValues.size(); i++) {
                ps.setObject(i + 1, realValues.get(i));
            }
            ps.executeUpdate();
        }
    }

    public void updateRow(String table, List<ColumnInfo> cols, List<Object> values, Object pkValue) throws SQLException {
        ColumnInfo pkCol = cols.stream().filter(ColumnInfo::isPk).findFirst().orElse(null);
        if (pkCol == null) throw new SQLException("No primary key");

        StringBuilder sbSet = new StringBuilder();
        List<Object> realValues = new ArrayList<>();

        for (int i = 0; i < cols.size(); i++) {
            ColumnInfo col = cols.get(i);
            if (col.isPk()) continue;
            if (sbSet.length() > 0) sbSet.append(", ");
            sbSet.append("\"").append(col.name()).append("\"=?");
            realValues.add(values.get(i));
        }

        String sql = "UPDATE \"" + table + "\" SET " + sbSet +
                " WHERE \"" + pkCol.name() + "\" = ?";
        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            int idx = 1;
            for (Object v : realValues) {
                ps.setObject(idx++, v);
            }
            ps.setObject(idx, pkValue);
            ps.executeUpdate();
        }
    }

    public void deleteRow(String table, List<ColumnInfo> cols, Object pkValue) throws SQLException {
        ColumnInfo pkCol = cols.stream().filter(ColumnInfo::isPk).findFirst().orElse(null);
        if (pkCol == null) throw new SQLException("No PK");

        String sql = "DELETE FROM \"" + table + "\" WHERE \"" + pkCol.name() + "\"=?";
        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setObject(1, pkValue);
            ps.executeUpdate();
        }
    }

    // ========== SEARCH ==========

    public TableDataModel search(String table,
                                 List<ColumnInfo> cols,
                                 String column,
                                 String pattern) throws SQLException {

        String sql = "SELECT * FROM \"" + table + "\" WHERE \"" + column + "\" LIKE ?";
        PreparedStatement ps = connection.prepareStatement(sql);
        ps.setString(1, "%" + pattern + "%");

        ResultSet rs = ps.executeQuery();
        return new TableDataModel(rs);
    }
}
