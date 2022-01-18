/*Script produtos*/
create database shop_produtos;

use shop_produtos;

create table produtos (
	id_produtos_PK int(100) auto_increment primary key,
    descricao varchar(100)
);
insert into produtos values
	(default, 'aparelho movel');