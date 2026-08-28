package com.omniclaim.app;

import java.io.Serializable;

public class ExpenseItem implements Serializable {
    public String id;
    public String description;
    public double amount_eur;

    public ExpenseItem(String id, String description, double amount_eur) {
        this.id = id;
        this.description = description;
        this.amount_eur = amount_eur;
    }
}
