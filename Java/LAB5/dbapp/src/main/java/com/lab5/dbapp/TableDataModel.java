package com.lab5.dbapp;

import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.util.ArrayList;
import java.util.List;

import javax.swing.table.AbstractTableModel;

public class TableDataModel extends AbstractTableModel {

    private final List<String> columnNames = new ArrayList<>();
    private final List<List<Object>> data = new ArrayList<>();
    private final List<ColumnInfo> columnsMeta = new ArrayList<>();
    private int pkIndex = -1;

    public TableDataModel(ResultSet rs) throws Exception {
        ResultSetMetaData md = rs.getMetaData();
        int colCount = md.getColumnCount();

        for (int i = 1; i <= colCount; i++) {
            String colName = md.getColumnName(i);
            String type = md.getColumnTypeName(i);

            columnNames.add(colName);

            boolean isPk = colName.equalsIgnoreCase("id");
            if (isPk) pkIndex = i - 1;

            columnsMeta.add(new ColumnInfo(colName, type, isPk));
        }

        while (rs.next()) {
            List<Object> row = new ArrayList<>();
            for (int i = 1; i <= colCount; i++) {
                row.add(rs.getObject(i));
            }
            data.add(row);
        }
    }

    public List<ColumnInfo> getColumnsMeta() {
        return columnsMeta;
    }

    public List<Object> getRow(int rowIndex) {
        return data.get(rowIndex);
    }

    public Object getValueAtRowPk(int rowIndex) {
        if (pkIndex == -1) return null;
        return data.get(rowIndex).get(pkIndex);
    }

    @Override
    public int getRowCount() {
        return data.size();
    }

    @Override
    public int getColumnCount() {
        return columnNames.size();
    }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {
        return data.get(rowIndex).get(columnIndex);
    }

    @Override
    public String getColumnName(int columnIndex) {
        return columnNames.get(columnIndex);
    }
}
