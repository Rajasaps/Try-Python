-- Database untuk Kedai Hauna POS System
-- Jalankan di phpMyAdmin (XAMPP)

CREATE DATABASE IF NOT EXISTS kedai_hauna;
USE kedai_hauna;

-- Tabel untuk menyimpan transaksi
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(100) DEFAULT 'Umum',
    payment_method VARCHAR(20) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel untuk menyimpan item transaksi
CREATE TABLE IF NOT EXISTS transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL,
    item_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    variant VARCHAR(50) DEFAULT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    INDEX idx_transaction_id (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel untuk menu items (opsional, untuk manajemen menu)
CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image_path VARCHAR(255),
    has_variant BOOLEAN DEFAULT FALSE,
    variants TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert menu items default
INSERT INTO menu_items (id, name, price, image_path, has_variant, variants) VALUES
(1, 'Bakso Malang', 23000, 'static/images/Bakso malang.jpg', FALSE, NULL),
(2, 'Seblak Special', 16000, 'static/images/Seblak special.jpg', FALSE, NULL),
(3, 'Mie Ayam', 18000, 'static/images/Mie Ayam.jpg', FALSE, NULL),
(4, 'Siomay', 11000, 'static/images/Siomay.jpg', FALSE, NULL),
(5, 'Tea', 6000, 'static/images/Tea.jpg', TRUE, 'Dingin,Hangat'),
(6, 'Ayam Crispy', 17000, 'static/images/Ayam Crispy.jpg', FALSE, NULL),
(7, 'Nasi', 5000, 'static/images/Nasi.jpg', FALSE, NULL);
