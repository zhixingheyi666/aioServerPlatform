/**
 0.0基于hash的算法肯定存在碰撞问题，这个是需要考虑的。
 0.由于自己数据库设计并不完善，所以很多缺陷要靠程序上的设计去补充。
    .例如，多种长度相仿的数据类型，如果能够转换成字符串存储的，就转换成字符串
      这样就可以统一存储在varchar类型的一列中。同时建立一个存储类型列，取用数据
      的时候，根据存储类型列，把取出的数据转换成相应类型的数据，我这样做意图减少
      表中列的数目。不知道是让很多列存在null，还是这个样子效率更高？
      eg:user_note表的format,data两列
    .例如，还有一个复用某一列的办法。在表table_info_note中，order的主要用意是标记
      每个对象中mate存取时候的迭代顺序，一般为正整数。如果我想复用这个列，可以规定
      正整数部分表示mate的迭代顺序，-1表示相应的mate处于删除或弃用的状态，-100 ~ -199
      表示对应的hash列存储的是remark的索引hash。对于remark来说，last_row一列可以标记成
      -100。
 1.每个存贮对象一个表。
 2.设立路径列，路径列一样，就属于同一个对象。
      考虑路径用什么作为分隔分隔符？
        例如用”.”号作为分隔符，那么路径的名称中不能出现“.”号
      或者在这样规模较小的表中，可以使用每一节路径的数字代码串联
      起来表示路径。
 3.设立键名称列，str，用于存储对象中每个键的名字。路径和名称列一样，
    即可判定为同一个<元>,我们这里记录<元>随时间的变化。
 4.设立时间列，以便追踪对象随时间的变化。
*/
/**
 5.考虑个别键的内容可能存在大块文本，可以设立转储表， 专用于存储大段文本
    或者考虑后来存储大块数据或者影像。
 6.最终是要达到<自动化> 的目的。例如传进来一个新对象，根据上述规则，自动建立相应
    的新表，自动填充表。目前表名的命名还是人工的，以后可以根据对象的唯一识别特征
    等自动命名。
 7.目前还不能做到全自动判定一个对象是否是全新的，我们可以基于对象的<元>并且<元>的
    路径结构来自动判定对象一致，要构造出对象的唯一识别特征码，但程序目前无法包含更大的外部环境信息，所以绝对的
    一致性还需要人工判定。
*/
/**
 9.对于这的数据，当然也可以采用分表然后联合查询的办法。例如数据值和时间两列单成一表。
    但这是数据量不大的小测试，加上自己不熟，暂时采用目前都在一表中的做法。
 10.有的时候，同一个对象有了一点点改动，例如增减了一两个小属性，或者重命名了一个属性，如果
    开发者主观上仍然要继续沿用旧表，该怎样兼容呢？可以单独记录哪些属性处于删除状态，但是
    并不真正删除数据，只是查询输出的时候，并不输出。也就是为传进来的对象内部自行增加了一个
    删除状态属性。当然这个测试暂不实现这个做法。
 11.为了快捷取出最后一次存储进去的对象数据，可以设置一个属性，记录最后存储的每个<元>的行号，
    取出时，直接查询指定行号，然后拼接即可。
 12.设置对象值类型列。在本次测试中，可以不设。原则上把所有的<元>的值都可以存储为str类型，因为
    对象都是通过json传过来的，也就是都是字符串化的。但是为以后扩展需要，可以设定此列。目前这列
    还有一个用处，就是区分<元>的值是另一个对象，还是一般的可以字符串化的值(bool,number,str,array)
    如果是对象，这一列的键值就是Object；还可以区分是<元>的值是否被转储，如果转储，这一列的值
    就是exStorage。
 13.通过测试JSON.stringfy函数得知，Json对象的所有键都被看做字符串对象，在json化的时候，都是
    用双引号包裹的，Json的键的值，如果是字符串，则会被双引号包裹，如果是一般的bool，则false
    字样不会被双引号包裹，同理数字类型也不会被双引号包裹。
    JSON.stringfy函数会把值为undefined的属性直接忽略掉，在转换后的字符串中，并不
    包含这个属性名。
*/
/**
 14.对于一个确定的对象，可以尝试建立他的<元>指纹迭代树，每次存取按照迭代指纹操作。
*/
/**
 a.a 数据行的总长度是受mysql行总size限制的。
 a.假定<元>键值中不存在双引号，存入之前进行检测，检测到报错。
 b.<元>键值(<元>的名称)name受数据库限制，5.0版本之后是长度不得超过255个字元
 c.<元>的路径path限制，5.0版本之后是长度不得超过800个字元
 c.<元>的值data限制，5.0版本之后是长度不得超过1200个字元
 d.由于是python驱动的，列名会映射成python对象，所以列名最好不要和python关键字重名
*/

/**
  ··
    这里涉及到的重要技术：
      ·对象唯一标识生成技术
      ·对象有序迭代技术
      ·对象一致性判定技术
*/

/**
  a.我设想把一个对象的本身信息，和我对这个对象的附加信息都整合进入这个表中。
    典型的对象附加信息，例如：这个对象中mate的迭代顺序，我对这个对象添加的
    注释，等等。为了区分原生信息和附加信息，可以吧mate_order列复用，mate_order
    如果为正整数，则视为对象的原生信息，如果为负数，则视为附加信息。
  b.根据原生信息和附加信息的设计结构，在对象存取时候，要设计两步处理流程。首先处理
   原生信息，以及会随原生信息随动的附加信息，进行存取，然后处理相对固定的附加信息，进行
   存取。至于那些附加信息是随动的，那些附加信息是固定的，在数据库中并未设定标志，是由
   程序逻辑代码所决定的。
  .根据以上设计，(path,mate,mate_order,order) 应该组成一个unique key
  c.附加信息概览：
    0.mate:***              path:***                    mate_order:-1
    这是个有序迭代属性，由于还未考虑周全，所以用***表示，我设想对于
    同一个对象，应该进行有序迭代，这个属性就存储有序迭代的相关信息，
    比如迭代顺序。我想利用已知的迭代顺序，方便的逆向从存储中把对象恢复出来。
    当然，也许不需要有序迭代，就能比较方便的恢复。
    1.mate:row_id           path:users_note.row_id      mate_order: -100
    某次存储时，所有原生信息的行id，我们可以同时按照迭代顺序来记录，这样这个值兼具有
    迭代顺序的功能。由于这些行数基本接近，可以采用记录一个基准数值，然后后面用正负
    于基准值的数字串来表示的办法。
    2.mate:remark           path: users_note.remark     mate_order: -200 ... -299
    3.mate:notObj           path:users_note.notObj      mate_order: -2
      如果传进来的是不是对象(准确的说，不是dict或者list)，就生成这个附加信息，并存储
      传进来的值。
*/
/**
  d.各列简介：
    mate_order:对象迭代写入数据库时候的顺序号，从1开始。
              其实也可以考虑字点分数字形式的字符串，例如3.14.2
              表示第一层第3个元素.第二层第14个元素.第三层第2个元素
              这一列的主要用途是取出对象的时候，可以方便的按照顺序
              直接拼装成json格式数据。
    order： 每存一次数据，该值增加1，相同的order表示是同一次的数据。如果
            要取出某次的数据，给出相应的order即可。
    mate_format: mate值类型列。原则上把所有的<元>的值都可以存储为str类型，因为
            对象都是通过json传过来的，也就是都是字符串化的。目前这列
            的用处，就是区分<元>的值是另一个对象，还是一般的可以字符串化的值(bool,number,str)
            如果是对象，这一列的键值就是Object，如果是Array，这一列的键值就是Array；还可以区分是<元>的值是否被转储，
            如果转储，这一列的值就是exStorage。
*/
use fortest;

create table users_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

create table user_urls_note(
  `id` int(11) unsigned not null auto_increment,
  `path` varchar(800) not null,
  `mate` varchar(255) not null,
  `mate_hash` BINARY(20) not null,
  `mate_order` SMALLINT  NOT NULL,
  `order` INT(11)  NOT NULL,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mate_format` varchar(30) not null,
  `data` VARCHAR(1200)  NULL ,
  UNIQUE (`path`,`mate_order`,`order`),
  KEY (`order`),
  primary key (`id`)
) engine = innodb default charset = utf8;

/*
··<<引用计数法则>>
*/
create table text_data_note(
  `data` MEDIUMTEXT not null,
  `data_hash` CHAR(64) NOT NULL,
  `quote` MEDIUMINT not NULL ,
  primary key (`data_hash`)
) engine = myisam default charset = utf8;

CREATE TABLE table_register_note(
  `table` VARCHAR(800) not null,
  `last_order` int(11) ,
  PRIMARY KEY (`table`)
) ENGINE  = innodb DEFAULT CHARSET = utf8;


-- ---------------------------------历史参考-----------------------------------------------------
/*
 8.可以设立一个<对象说明总表>，里面包含所有对象的唯一识别特征，然后给每个对象基于时间的无限制的注释
    说明，概况信息，一切想要额外说明的内容都可以记录在这里。

*/
/**
  CREATE TABLE index_user_id (
    user_id BINARY(16) NOT NULL,
    entity_id BINARY(16) NOT NULL UNIQUE,
    PRIMARY KEY (user_id, entity_id)
) ENGINE=InnoDB;
*/
/**
 *.object_info_note 说明
    obj_name：存储的对象的名字或其他唯一识别标志
              这个名字还是为存储这个对象建立的专门的表的名字。
    obj_mate_hash：每个对象中的每个key(包含完整路径的key)的hash值，可以唯一标志
              对象结构中的每一个节点。
    order__type：的主要用意是标记每个对象中mate存取时候的迭代顺序，一般为正整数。
              我想复用这个列，可以规定正整数部分表示mate的迭代顺序
                ，0表示对象的唯一识别特征（其实唯一识别特征应该单独成列）
                ，-1表示相应的mate处于删除或弃用的状态
                ，-100 ~ -199表示对应的hash__data列存储的
                      是remark的索引hash。另外对于remark来说，last_row一列可以标记成-100。
*/
/**
create TABLE object_info_note(
  `id` int(11) unsigned not null auto_increment,
  `obj_name` char NOT NULL ,-- 名字不能重复
  `hash__data` BINARY(16) not null,
  `order__type` SMALLINT  NOT NULL,
  `last_row` int(11) NOT NULL
);
*/


