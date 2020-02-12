# python + pymysql 创建数据库 
import pymysql
# 创建连接
conn = pymysql.connect(host='localhost',user='root',password='123wangchao',db='mysql',charset='utf8')
# 创建游标
cursor = conn.cursor()
 
# 创建数据库的sql(如果数据库存在就不创建，防止异常)
sql = "CREATE DATABASE IF NOT EXISTS testdb2020" 
# 执行创建数据库的sql
cursor.execute(sql)
conn.commit()
print('新建的数据库名为：testdb2020')
conn.close()
# 在新建的数据库上新建表
conn = pymysql.connect(host='localhost',user='root',password='123wangchao',db='testdb2020',charset='utf8')
cursor = conn.cursor()
# 创建表
sql_2 = '''CREATE TABLE `employee` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `topic` INT ,
  `ptid` INT NOT NULL,
  `level` INT NOT NULL,
  `time` TIME,
  `consume` INT NOT NULL,
  `err` INT NOT NULL,
  `points` INT NOT NULL,
  `gid` INT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
cursor.execute(sql_2)
conn.commit()
print('新建的表名为：employee')
conn.close()