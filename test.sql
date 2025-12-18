CREATE DATABASE IF NOT EXISTS ragmysqldb;
USE ragmysqldb;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
 );

INSERT INTO categories (category_name) VALUES
 ('Shirts'),
 ('Pants'),
 ('Dresses'),
 ('Jackets'),
 ('T-Shirts');

CREATE TABLE brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(50) NOT NULL
);

INSERT INTO brands (brand_name) VALUES
('Nike'),
('Adidas'),
('Zara'),
('H&M'),
('Puma');

CREATE TABLE clothes (
    cloth_id INT AUTO_INCREMENT PRIMARY KEY,
    cloth_name VARCHAR(100) NOT NULL,
    category_id INT,
    brand_id INT,
    size VARCHAR(10),
    color VARCHAR(30),
    price DECIMAL(10,2),
    stock_quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id)
);

INSERT INTO clothes
(cloth_name, category_id, brand_id, size, color, price, stock_quantity)
VALUES
('Men Casual Shirt', 1, 3, 'M', 'Blue', 2999.00, 20),
('Women Summer Dress', 3, 4, 'S', 'Red', 3499.00, 15),
('Men Sports T-Shirt', 5, 1, 'L', 'Black', 1999.00, 30),
('Women Jacket', 4, 2, 'M', 'Grey', 4999.00, 10),
('Men Slim Fit Pants', 2, 5, '32', 'Navy', 3999.00, 12);





