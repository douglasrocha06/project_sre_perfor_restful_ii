/*Script clientes*/
create database shop_clientes;

use shop_clientes;

create table clientes (
	id_clientes_PK int(100) auto_increment primary key,
    nome varchar(100)
);
insert into clientes values
	(default, 'Douglas Cristhian dos Santos');
    