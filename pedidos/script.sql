/*Script pedidos*/
create database shop_pedidos;

use shop_pedidos;

create table pedidos (
	id_pedidos_PK int(100) auto_increment primary key,
	id_clientes_FK int(100),
	id_produtos_FK int(100)
);
insert into pedidos values
	(default, 1, 1);