CREATE DATABASE IF NOT EXISTS order_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE order_db;

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(16) PRIMARY KEY,
    customer_id VARCHAR(16) NOT NULL,
    customer_email VARCHAR(254) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    items_count INT NOT NULL,
    INDEX idx_orders_customer (customer_id),
    CONSTRAINT chk_order_amount CHECK (total_amount >= 0),
    CONSTRAINT chk_order_items CHECK (items_count > 0)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(16) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    brand VARCHAR(80) NOT NULL,
    category VARCHAR(40) NOT NULL,
    price_inr DECIMAL(12, 2) NOT NULL,
    capacity_l INT NOT NULL,
    weight_g INT NOT NULL,
    height_cm INT NOT NULL,
    width_cm INT NOT NULL,
    depth_cm INT NOT NULL,
    description TEXT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id VARCHAR(16) PRIMARY KEY,
    order_id VARCHAR(16) NOT NULL,
    product_id VARCHAR(16) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    UNIQUE KEY uq_order_product (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_item_quantity CHECK (quantity > 0),
    CONSTRAINT chk_item_price CHECK (unit_price >= 0)
) ENGINE=InnoDB;
