# Weekly Assignment 5

**by Fathurrahman Hernanda Khasan DF12**
# Database Documentation

This document provides documentation for the database schema including dimension tables, fact table, their relationships, and the Entity-Relationship Diagram (ERD).

## Dimension Tables:

1. **Customer Dimension**:
   - **customer_id (PK)**: Primary key that uniquely identifies each customer.
   - **customer_name**: Customer's name.
   - **age**: Customer's age.
   - **gender**: Customer's gender.
   - **zipcode**: Customer's zip code.

2. **Merchant Dimension**:
   - **merchant_id (PK)**: Primary key that uniquely identifies each merchant.
   - **merchant_name**: Merchant's name.
   - **zipmerchant**: Merchant's zip code.

3. **Category Dimension**:
   - **category_id (PK)**: Primary key that uniquely identifies each category.
   - **category_name**: Category's name.

## Fact Table:

4. **Transaction Fact**:
   - **transaction_id (PK)**: Primary key that uniquely identifies each transaction.
   - **step**: Step in the transaction.
   - **customer_id (FK)**: Foreign key linking to the Customer Dimension table.
   - **merchant_id (FK)**: Foreign key linking to the Merchant Dimension table.
   - **category_id (FK)**: Foreign key linking to the Category Dimension table.
   - **amount**: Transaction amount.
   - **fraud**: Indicator of whether the transaction is fraudulent (0 for no, 1 for yes).

## Relationships:

1. The relationship between **Transaction Fact** and **Customer Dimension** is **many-to-one (1-to-many)** because many transactions can be done by one customer, but one transaction can only have one customer.

2. The relationship between **Transaction Fact** and **Merchant Dimension** is also **many-to-one (1-to-many)** because many transactions can be done at one merchant, but one transaction can only be done at one merchant.

3. The relationship between **Transaction Fact** and **Category Dimension** is also **many-to-one (1-to-many)** because many transactions can fall into one category, but one transaction can only fall into one category.

## Entity-Relationship Diagram (ERD):
```lua
-- Entity-Relationship-Diagram Banksim_Artificial

+-----------------+          +-------------------+          +----------------+
| Customer        |          | Transaction       |          | Merchant       |
+-----------------+          +-------------------+          +----------------+
| customer_id (PK)|*--------1| transaction_id (PK)|1--------*| merchant_id (PK)|
| customer_name   |          | step              |          | merchant_name   |
| age             |          | customer_id (FK)  |----------| zipmerchant     |
| gender          |          | merchant_id (FK)  |          +----------------+
| zipcode         |          | category_id (FK)  |*---------1
+-----------------+          | amount            |          |
                              | fraud             |          |
                              +-------------------+          |
                                                              |
                              +-------------------+          |
                              | Category          |          |
                              +-------------------+          |
                              | category_id (PK)  |*--------1|
                              | category_name    |          |
                              +-------------------+          |

```

```vbnet
This is a visual representation of the ERD 
Showing the relationships between the customer dimension, 
Transaction dimension, merchant dimension, and category dimension. 
The lines connecting the tables indicate the foreign key-primary key relationship between the tables.

With these dimension and fact tables, 
You can perform better and more structured data analysis 
On transactions and customer as well as merchant information.
```


![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/e596239c-b06c-4526-9534-6e82adaf9ace)


Pada Projek kali ini saya akan membuat pipline ETL sederhana dengan kriteria: 

1. Data dari csv pada folder weekly assignment di load pada postgresQL local

machine.

2. Kemudian melakukan transformasi, filtering, enriching data.

3. Setelah datanya bersih, atau sesuai yang dikehendaki, load ke Cloud.

SQL di google cloud platform dengan nama table yang sama.

4. Setelah datanyanya landing pada Cloud SQL, offload ke BigQuery secara as is

atau apa adannya.

### Tambahan dokumentasi Untuk proyek ini diberi dokumentasi di github:

### Keterangan transformasi sampai settingan databasenya, data catalognya, data modelnya.

Oke langsung saja berikut Penjelasannya dalam penjelasan ini aku bagi penjelasannya menjadi 3 section Yaitu:

1. **Section 1 “Extract”**
2. **Section 2 “Transform”**
3. **Section 3 “Load”**

# Extract

Pada proses Extract disini saya melakukannya dengan mengambil data banksim_artificial.csv yang disediakan oleh mentor. pertama tama pada proses ekstract saya mengconnectkan data banksim_artificial.csv tadi ke jupyter notebook saya menggunakan psycopg2 dan membaca dataframenya menggunakan pandas.

Mengconnectkan database menggunakan psycopg2:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/3aa26efc-f780-4f9e-9f16-8cf5f3b071b9)


Melhat Karakteristik:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/a7d50767-60ed-417c-8a08-8079360f6353)


Setelah dilihat bahwa terlihat jelas ya bahwa dataset ini masih belum begitu clean ya bisa dilihat penggunaan tipe data dan bentuk dari dataset masih mengandung karakter yang tidak diperlukan oleh karena itu nanti akan kita bersihkan di saat proses transformasi namun sebelum itu kita perlu membuat table untuk menampung dile dataset ini:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/c2e6327a-8a0d-48d5-b7d5-39e8275324bf)


Setelah tabel selesai dibuat baru masukkan data banksim_artificial.csv ke dalam database tersebut:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/5d1b6f1e-1cfb-411d-83ee-52ddf9f974fa)


# Transform

Setelah dataset di load ke database saatnya kita melakukan transform data, masih ingatkan sebelumnya bahwa data yang kita pakai disini masih kotor oleh karena itu kita perlu membersihkannya agar enak digunakan untuk analytics.

pertama-tama untuk membersihkan data ini saya menghilangkan dan mengubah karakter yang tidak penting di database:

Menghilangkan tanda (“”) yang tidak perlu:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/56d596b0-9115-4048-8767-b83a91cd1514)


Setelah itu Saya melihat ada anomaly di gender yaitu terdapat nilai U di gender oleh karena itu saya melakukan karena terdapat nilai ‘U’ disana maka selanjutnya saya mengubah kareakter ini ke angka ‘2’ atau modus dan rata rata dari age.

Alasan mengapa menggunakan modus atau rata-rata adalah pilihan yang masuk akal untuk mengganti nilai 'u' dalam data usia yang salah. Tujuannya adalah untuk memberikan representasi yang masuk akal dari data usia yang valid tanpa memperkenalkan bias yang signifikan.  

Anomaly data:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/c8156256-52fc-4f49-8549-3a908f6ec53c)


Transformasi nilai yang anomaly:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/3efa3a1c-b0ff-465c-bcb8-0120e8306f87)


setelah melakukan hal ini sebenarnya masih ada yang anomaly lagi yaitu bagian kedua zipcode disana keduanya memiliki nilai yang sama semuanya namun karena saya disini bertugas sebagai data engineer saya mentransformasikan data tersebut lebih ke mengubah tipe datanya saja dan untuk menghandle hal ini saya lebih percaya ke data analyst atau data scientist yang transformasi karena mungkin saja ini adalah data yang penting jadi saya tidak drop kolomnya dan hanya mengubah tipe datanya saja.

Update datatype zipcode:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/67347ae0-b871-4401-9998-e86caa8bf872)


Update data type age yang sebelumnya yang masih varchar atau string di transformasikan ke small integer: 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/ea5c5748-a47d-4ef9-a60f-a33f89a5f3ae)


Nah untuk validasi dan pengecekan apakah datanya sudah bersih dan siap dimasukkan ke staging atau cloud sql atau ke data warehouse di bigquey disini saya kembali menggunakan pandas.

Cek tabel:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/9cf66f8a-faa4-4737-820a-71aef2e2e15f)


Cek statistik dan data type:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/0073fe5c-5d6e-4b60-b11a-6021bae78ebf)


Cek Null value:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/7d1b0e92-dd82-4020-a35f-f73b150d49f6)


Nice mantap kita telah menyelesaikan transformasi datanya dengan maksimal semoga dengan ini data analyst dan data scientist nyman menggunakan data ini 😁. Oke saatnya masuk ke proses terakhir yaitu Load.

# **Load**

Proses Load disini ada 2 objektif yaitu data di load ke staging area yaitu google cloud sql kemudian data di load ke data warehouse, pada kasus ini data warehousenya adalah google bigquery.

Untuk load data ke google cloud sql disini saya menggunakan treatment yaitu dengan file sql yang dibuat dari database on premise saya yang dibantu dengan comment pg_dump yang di konfig sesuai gcp. berikut untuk dokumentasi lebih jelasnya confignya seperti apa:

[Export and import using pg_dump, pg_dumpall, and pg_restore  |  Cloud SQL for PostgreSQL  |  Google Cloud](https://cloud.google.com/sql/docs/postgres/import-export/import-export-dmp)

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/c9dba837-90f0-4014-b3d1-84471cfaa73c)


Sebelum itu kita juga perlu membuat GCS bucket untuk menampung dan upload file .sql:

Membuat GCS bucket:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/d068ae1f-2e1b-4ea2-9578-bcaeed4c8877)


Upload file ke GCS:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/12e411c9-dc4f-4f00-b6d2-012dcc5ad029)


Dan pada tahap ini kita perlu setup google cloud sqlnya terlebih dahulu dengan create instance.

Create instance dan pilih postgreSQL:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/aea76941-6a39-4a01-9aec-91d1672d821e)


Pilih Memory sesuai data yang digunakan disini saya memilih yang paling kecil karena sudah cukup dan untuk meminimalkan cost.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/262c86cc-621f-4fb6-8738-337542aa8b57)


Tunggu hingga Instance berhasil dibuat.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/31c5b561-67c3-4c64-96ff-b658be763203)


Kemudian masuk kedalam instance cloud sql tersebut:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/c789e865-17a3-4fde-a74f-dc3076001dcd)


Dan pilih file pg_dump .sql yang telah di upload ke GCS sebelumnya.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/34c3562e-bf99-467f-8333-89d9378602eb)


Pilih file format SQL

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/2a797101-95d1-4e7f-a31d-1fca387c6ac4)


Tunggu hingga selesai lalu pergi ke cloud system studio untuk cek data masuk atau belum:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/ab228a2c-519e-4012-9936-14ef612d93bf)


jika sudah query saja sesukanya untuk cek datanya dan pastikan datanya sesuai.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/2cb00ef6-b3c5-4c95-b300-d8fcb724d1a7)


Setelah selesai load data ke cloud sql selanjutnya kita akan melaksanakan objective kedua yaitu connecting data yang ada di cloud sql dan dipindahkan ke google bigquery maka dari itu langkah pertama yang harus dilakukan adalah Create dataset di google bigquey terlebih dahulu:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/0d775f1a-f247-4b7a-90ad-f5d7adb7b4d2)

Kemudian create table dengan kolom dan tipe data yang sesuai:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/8b09af78-a9e0-458a-9031-516a373e2d8d)


jika sudah connectkan dengan tools dataflow dan create job:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/57367147-b9c1-4ce4-9c64-bb688e5f9b5b)


atur target dan flow yang diinginkan disini saya menggunakan template dari GCP postgre to Bigquery lalu isi sesuai spesifikasimu lalu run job:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/9db351f6-ab15-45e0-babc-1b2e380ff600)


## Alternatif ke dua menggunakan Google DataStream

Jika menggunakan dataflow dianggap lebih susah dan ribet confignya ada alternatif lain dan kebetulan disini saya lebih fokus menggunakan ini dalam pipeline saya yaitu menggunakan datastream.

Pertama-tama cari datastream di search bar kemudian hidupkan APInya agar bisa digunakan:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/de049538-aebe-46da-9412-518bdb8d83e6)


Kemudian create stream:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/d04669b1-d19d-4257-830d-b41f9bfbf486)


Kemudian isi configurasi sesuai yang diperlukan dan pilih source postgresql dan destinationnya adalah bigquery sesuai target dari pipeline ini: 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/d2503403-cf92-42dd-bda1-e209901a8391)


Kemudian isi kredensial yang sesuai target, dalam hal ini postgresql di cloud sql:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/73f1bced-5f5e-499f-ac66-67e280b7804f)


Kemudian define connectivity methodnya disini saya memilih ip allowlisting dan pilih lokasi servernya ketika sudah akan muncul 5 server setelah itu jangan lupa untuk memasukkan kelima koneksi tadi ke connections cloud sql supaya servicenya bisa saling berkomunkasi, lalu save.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/cf2357ed-baac-4042-9e18-22931e565039)


Kemudian test konesinya pastikan ‘Test passed’: 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/5b0ed274-4120-45d4-82dd-d150a3094a65)

Pada bagian configure source masukan nama dari koneksi yang ingin dibuat dan pilih shema database dan tabel mana yang ingin di replikasi:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/8c66b9fe-1130-4b2f-a722-57c69bcea696)


Disini juga bisa mengecek column selection dan pastikan pilih yang ingin direplikasi kalau saya disini ingin mereplikasi semua kolomnya:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/66b724dd-074b-4bd1-8f6d-7f41f84dbda1)


Setelah dari bagian configure source anda bisa ke bagian define destination dan isi communication profile name dan idnya:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/787da2df-b398-4812-944a-445f688de1eb)


Lanjut ke configure destination dan isi sesuai keperluan:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/75856db5-9760-4423-b31a-34eb63d6790d)


![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/596b8e5f-1101-497d-b10c-44f4daa742e5)


lalu pilih waktu untuk trigger bahkan bisa realtime streaming namanya saja data stream🙂:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/da34fc85-9a79-4aaf-8ce1-3d241f426f14)


kemudian review dan run validation: 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/8e9ad1d8-793b-4c10-bab2-bc1bdbbc241d)


Ini dia pentingnya validasi bisa dilihat dibawah ini ada beberapa fungsi yang tidak tervalidasi, dan jika ada yang memiliki permasalahan seperti dibawah bisa ikuti cara setelah ini, so jan lupa untuk ck dan validasi sebelum deploy.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/cc652f2a-b454-4443-be04-6a55b2245ab9)


Permasalahan sebelumnya terjadi karena ada beberapa fungsi yang belum saya config di bagian get started oleh karena itu perlu beberapa penyesuaian configurasi terutama di bagian permissions dan ikuti dengan baik prerequisitenya dari awal hingga akhir yang dikonfigurasi di postgresql cloud sql. 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/01a17d5f-077e-4875-9e3c-5afd3717dcb6)


![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/2a9391cb-ce3b-4c31-abf6-819b0212b10b)

Jika sudah lakukan validasi lagi maka niscaya validation run complate semua 😀. 

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/371c4a09-aca1-4b1c-9acb-53badffcd212)


Kemudian lakukan create dan start:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/450ee6f3-e3d9-4a78-a1af-6b160390829d)


dan pastikan statusnya berubah yang sebelumnya startting menjadi running:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/e57df4b3-2264-4219-b0f1-b872fb16d56e)


Last kamu bisa cek di google bigquery dengan melakukan select all, dan pastikan data sudah masuk semuanya.

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/6fbc5544-88b2-4951-91c9-ca122efd8450)

Jadi itu adalah gambaran singkat dokumentasi pembuatan simple pipeline ETL dari postgresql onpremise hingga ke data warehouse, berikut adalah gambar pipeline yang telah dibuat sebelumnya:

![image](https://github.com/fahernkhan/Weekly-Assignment5/assets/128980804/72451121-2caf-4bba-b1da-78892aa7a818)



keterangan: 

1. Mengambil dataset berbentuk csv.
2. Memasukkan dataset ke database (postgresql).
3. Transformasi data dari tipe data dan proporsi agar menjadi lebih bersih.
4. Memasukkan data berbentuk sql dari database on premise ke Google Cloud Storage.
5. Memasukkan atau migrasi data dari databse on premise yang sudah di transformasi yang disimpan ke gcs ke postgre sql cloud sql sebagai data staging.
6. Mengatur aliran data dalam sistem menggunakan dataflow, atau menggunakan datastream untuk mengalirkan  data secara terus-menerus yang memungkinkan analisis real-time.
7. Menyimpan data akhir ke data warehouse yaitu google bigquery. 

Bisa disimpulkan pipeline ini memulai dengan pengambilan dataset dalam format CSV, kemudian memasukkan dataset ke database PostgreSQL. Selanjutnya, dilakukan transformasi data untuk membersihkan tipe data dan proporsi. Data yang telah diubah kemudian dimasukkan ke Google Cloud Storage dalam format SQL dari database on premise. Proses migrasi data dari database on premise yang telah diubah ke PostgreSQL Cloud SQL dilakukan sebagai data staging. Aliran data dalam sistem dapat diatur menggunakan Dataflow atau menggunakan Datastream untuk analisis real-time. Akhirnya, data disimpan ke data warehouse Google BigQuery.

link code: [https://github.com/fahernkhan/Weekly-Assignment-IYKRA](https://github.com/fahernkhan/Weekly-Assignment-IYKRA)

thanks🦄
