## 3 Python代码风格规范

--------------------
### 3.1 分号
不要在行尾加分号，也不要用分号把两行语句合并到一行。

### 3.2 行长度
最大行长度是*80个字符*。

行长度超出80字符的例外：
* 长import表达式
* 注释中的：URL，路径，flags等
* 不包含空格并不方便分行的模块级别的长字符串常量
  * pylint的diable注释使用(如`# pylint: disable=invalid-name`)

不要使用反斜杠连接不同的行，除非对于需要三层或以上的上下文管理器`with`语句。

充分利用Python的[implicit line joining inside parentheses, brackets and braces](http://docs.python.org/reference/lexical_analysis.html#implicit-line-joining)（译者注：隐式行连接方法--括号连接,包括`(), [], {}`）。如果必要的话，也可在表达式外面额外添加一对括号。

**Yes:**
```Python
foo_bar(self, width, height, color='black', design=None, x='foo',
        emphasis=None, highlight=0)

if (width == 0 and height == 0 and
    color == 'red' and emphasis == 'strong'):
```

当字符串不能在一行内完成时，使用括号来隐式连接行：

```Python
x = ('This will build a very long long '
     'long long long long long long string')
```

在注释内,如有必要,将长URL放在其本行内:

**Yes:**
```Python
# See details at
# http://www.example.com/us/developer/documentation/api/content/v2.0/csv_file_name_extension_full_specification.html
```

**No:**
```Python
# See details at
# http://www.example.com/us/developer/documentation/api/content/\
# v2.0/csv_file_name_extension_full_specification.html
```

当`with`表达式需要使用三个及其以上的上下文管理器时，可以使用反斜杠换行。若只需要两个，请使用嵌套的with。

**Yes:**
```Python
with very_long_first_expression_function() as spam, \
     very_long_second_expression_function() as beans, \
     third_thing() as eggs:
    place_order(eggs, beans, spam, beans)

with very_long_first_expression_function() as spam:
    with very_long_second_expression_function() as beans:
        place_order(beans, spam)
```

**No:**
```Python
with VeryLongFirstExpressionFunction() as spam, \
     VeryLongSecondExpressionFunction() as beans:
    PlaceOrder(eggs, beans, spam, beans)
```
注意上述例子中的缩进，具体参看[缩进](https://google.github.io/styleguide/pyguide.html#s3.4-indentation)部分的解释。

在其他一行超过80字符的情况下，而且[yapf](https://github.com/google/yapf/)自动格式工具也不能使分行符合要求时，允许超过80字符限制。

### 3.3 括号
合理的使用括号。

尽管不必要，但是可以在元组外加括号。再返回语句或者条件语句中不要使用括号，除非是用于隐式的连接行或者指示元组。

**Yes:**
```Python
if foo:
    bar()
while x:
    x = bar()
if x and y:
    bar()
if not x:
    bar()
# For a 1 item tuple the ()s are more visually obvious than the comma.
onesie = (foo,)
return foo
return spam, beans
return (spam, beans)
for (x, y) in dict.items(): ...
```

**No:**
```Python
if (x):
    bar()
if not(x):
    bar()
return (foo)
```

### 3.4 缩进
缩进用4个空格。

缩进代码段不要使用制表符，或者混用制表符和空格。如果连接多行，多行应垂直对齐，或者再次4空格缩进，这个情况下首行括号后应该不包含代码。

**Yes:**
```Python
# Aligned with opening delimiter
foo = long_function_name(var_one, var_two,
                         var_three, var_four)
meal = (spam,
        beans)

# Aligned with opening delimiter in a dictionary
foo = {
    long_dictionary_key: value1 +
                         value2,
    ...
}

# 4-space hanging indent; nothing on first line
foo = long_function_name(
    var_one, var_two, var_three,
    var_four)
meal = (
    spam,
    beans)

# 4-space hanging indent in a dictionary
foo = {
    long_dictionary_key:
        long_dictionary_value,
    ...
}
```

**No:**
```Python
# Stuff on first line forbidden
foo = long_function_name(var_one, var_two,
    var_three, var_four)
meal = (spam,
    beans)

# 2-space hanging indent forbidden
foo = long_function_name(
  var_one, var_two, var_three,
  var_four)

# No hanging indent in a dictionary
foo = {
    long_dictionary_key:
    long_dictionary_value,
    ...
}
```

#### 3.4.1 序列元素尾部逗号
仅当`]`，`)`或者`}`和最后元素不在同一行时，推荐使用序列元素尾部逗号。尾后逗号的存在也被用作Python代码自动格式化工具[yapf](https://github.com/google/yapf/)的提示，在`,`最后元素出现之后来自动调整容器每行一个元素。

**Yes:**
```Python
golomb3 = [0, 1, 3]
golomb4 = [
    0,
    1,
    4,
    6,
]
```

**No:**
```Python
golomb4 = [
    0,
    1,
    4,
    6
]
```

### 3.5 空行
在顶级定义（函数或类）之间要间隔两行。在方法定义之间以及`class`所在行与第一个方法之间要空一行，`def`行后无空行，在函数或方法内你认为合适地方可以使用单空行。

### 3.6 空格
按照标准的排版规范来使用标点两边的空格。

括号`()`，`[]`，`{}`内部不要多余的空格。

**Yes:**
```Python
spam(ham[1], {eggs: 2}, [])
```

**No:**
```Python
spam( ham[ 1 ], { eggs: 2 }, [ ] )
```

逗号、分号、冒号之前不要空格，但应该在它们后面加（除了在行尾不该加）。

**Yes:**
```Python
if x == 4:
    print(x, y)
x, y = y, x
```

**No:**
```Python
if x == 4 :
    print(x , y)
x , y = y , x
```

参数列表，索引或切片的左括号之前不应加空格。

**Yes:**
```Python
spam(1)
```

**No:**
```Python
spam (1)
```

**Yes:**
```Python
dict['key'] = list[index]
```

**No:**
```Python
dict ['key'] = list [index]
```

行尾不要加空格。

在赋值(`=`)，比较（`==`，`<`，`>`，`!=`，`<>`，`<=`，`>=`，`in`，`not in`，`is`，`is not`），布尔符号（`and`，`or`，`not`）前后都加空格。视情况在算术运算符（`+`，`-`，`*`，`/`，`//`，`%`，`**`，`@`）前后加空格。

**Yes:**
```Python
x == 1
```

**No:**
```Python
x<1
```

当给关键字传值的时候或者是定义默认参数值的时候，不能在`=`前后加空格。只有一个情况例外：[当类型注释存在时](https://google.github.io/styleguide/pyguide.html#typing-default-values)，*一定要*在定义默认参数值时`=`前后加空格。

**Yes:**
```Python
def complex(real, imag=0.0): return Magic(r=real, i=imag)
def complex(real, imag: float = 0.0): return Magic(r=real, i=imag)
```

**No:**
```Python
def complex(real, imag = 0.0): return Magic(r = real, i = imag)
def complex(real, imag: float=0.0): return Magic(r = real, i = imag)
```

不要用空格来垂直对齐多行间的标记，因为这会成为维护的负担（适用于`:`，`#`，`=`等）：

**Yes:**
```Python
foo = 1000  # comment
long_name = 2  # comment that should not be aligned
dictionary = {
    'foo': 1,
    'long_name': 2,
}
```

**No:**
```Python
foo       = 1000  # comment
long_name = 2     # comment that should not be aligned

dictionary = {
    'foo'      : 1,
    'long_name': 2,
}
```

### 3.7 Shebang
大部分`.py`文件不必以`#!`作为文件的开始。根据[PEP-394](https://www.google.com/url?sa=D&q=http://www.python.org/dev/peps/pep-0394/)，程序的main文件应该以`#!/usr/bin/python2`或`#!/usr/bin/python3`起始。

（译者注：在计算机科学中，[Shebang](https://en.wikipedia.org/wiki/Shebang_(Unix))（也称为`Hashbang`）是一个由井号和叹号构成的字符串行（#!），其出现在文本文件的第一行的前两个字符。在文件中存在Shebang的情况下，类Unix操作系统的程序载入器会分析Shebang后的内容，将这些内容作为解释器指令，并调用该指令，并将载有Shebang的文件路径作为该解释器的参数。例如，以指令`#!/bin/sh`开头的文件在执行时会实际调用`/bin/sh`程序。）

`#!/usr/bin/python3`类似的行参数用于帮助内核找到Python解释器，但是在导入模块时，将会被忽略。因此只有被直接执行的文件中才有必要加入`#!`。

### 3.8 注释和文档字符串
确保对模块，函数，方法的文档字符串和行内注释使用正确的风格。

#### 3.8.1 文档字符串
Python使用*文档字符串（docstrings）*来为代码生成文档。文档字符串是包，模块，类或函数里的第一个语句。这些字符串可以通过对象的`__doc__`成员被自动提取，并且被`pydoc`所用（尝试在你的模块上运行`pydoc`来看看效果）。我们对文档字符串的惯例是使用三重双引号`"""`（根据[PEP-257](https://www.google.com/url?sa=D&q=http://www.python.org/dev/peps/pep-0257/)）。 一个文档字符串应该这样组织：一行概述，该行以句号，问号或者感叹号作为结尾（单行不能超过80个字符）；接着是一行空行，随后是剩下的文档字符，这些剩下的文档字符串应当与第一行的第一个引号对齐。下面有更多文档字符串的格式化规范。

#### 3.8.2 模块
每个文件都应包含开源许可模板。选择用于项目的合适的开源许可模板（例如
Apache 2.0，BSD，LGPL，GPL）

文档应该以文档字符串开头，并描述模块的内容和使用方法。
```Python
"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""
```

#### 3.8.3 函数和方法
在本节，"函数"所指包括方法，函数或者生成器。

函数必须具有文档字符串（docstring），除非有以下情况的出现：
* 外部不可见
* 非常短小
* 简单明了

文档字符串应该给出足够的信息，在不需要阅读函数代码的情况下说清如何调用该函数。文档字符串应该是叙事体（`"""Fetches rows from a Bigtable."""`）的而非命令式的（`"""Fetch rows from a Bigtable."""`），除非是`@property`（应与[attribute](https://google.github.io/styleguide/pyguide.html#384-classes)使用同样的风格）。文档字符串应描述函数的调用语法和其意义，而非实现。对于比较有技巧性的代码，代码旁边加注释比文档字符串的方法要更合适。

覆盖基类的子类方法应有一个类似于`See base class`的简单注释来指引读者到基类方法的文档注释。这是因为子类方法没有必要在很多地方重复已经存在的基类的文档。但是，如果子类覆写的方法的行为与基类方法的行为有很大不同，那么注释中应该说明这些细节（例如，文档中说明副作用），覆写方法的文档字符串至少应该包含这些细节信息。

关于函数的几个特定的方面应该在特定的小节中进行描述记录，这几个方面如下所述：每节应该以一个标题行开始，标题行以冒号结尾，每一节除了首行外，都应该以2或4个空格缩进并在整个文件内保持一致（译者注：包括与代码的缩进保持一致）。如果函数名和签名足够给出足够信息并且能够刚好被一行文档字符串所描述，那么可以忽略这些节：

[*Args:*](https://google.github.io/styleguide/pyguide.html#doc-function-args)

列出每个参数的名字。对参数的描述应该紧随参数名，并且使用一个冒号跟着空格或者一个冒号随后另起一行来分隔参数名与描述。如果描述太长了不能满足单行80个字符的要求，那么分行并缩进2或4个空格的悬挂缩进（必须与整个文件一致）。描述应该包含参数所要求的类型，如果代码不包含类型注释的话。如果函数容许`*foo`（不定长度参数列表）或`**bar`（任意关键字参数），那么就应该在文档字符串中列举为`*foo`和`**bar`。

[*Returns:(对于生成器是Yields:)*](https://google.github.io/styleguide/pyguide.html#doc-function-returns)

描述返回值的类型和含义。如果函数只返回None，这一小节不需要。如果文档字符串以Returns或者Yields开头（例如`"""Returns row from Bigtable as a tuple of strings."""`）或首句足够描述返回值的情况下，这一节可忽略。

[*Raises:*](https://google.github.io/styleguide/pyguide.html#doc-function-returns)

列出所有和接口相关的异常。使用与*Args:*一节中相似的形式描述异常，如异常名字+冒号+空格或者悬挂缩进。对于违反API要求而抛出的异常不应列出（因为这会悖论地使得违反API要求的行为成为接口的一部分）。

```Python
def fetch_smalltable_rows(table_handle: smalltable.Table,
                          keys: Sequence[Union[bytes, str]],
                          require_all_keys: bool = False,
    ) -> Mapping[bytes, Tuple[str]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table row to fetch.  String keys will be UTF-8 encoded.
        require_all_keys: Optional; If require_all_keys is True only rows with values set for all keys will be returned.

    Returns:
        A dict mapping keys to the corresponding table row data fetched. Each row is represented as a tuple of strings. For example:

        {b'Serak': ('Rigel VII', 'Preparer'),
        b'Zim': ('Irk', 'Invader'),
        b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is missing from the dictionary, then that row was not found in the table (and require_all_keys must have been False).

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
```

在`Args:`上进行换行也是可以的：

```Python
def fetch_smalltable_rows(table_handle: smalltable.Table,
                          keys: Sequence[Union[bytes, str]],
                          require_all_keys: bool = False,
    ) -> Mapping[bytes, Tuple[str]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle:
            An open smalltable.Table instance.
        keys:
            A sequence of strings representing the key of each table row to fetch.  String keys will be UTF-8 encoded.
        require_all_keys:
            Optional; If require_all_keys is True only rows with values set for all keys will be returned.

    Returns:
        A dict mapping keys to the corresponding table row data fetched. Each row is represented as a tuple of strings. For example:

        {b'Serak': ('Rigel VII', 'Preparer'),
        b'Zim': ('Irk', 'Invader'),
        b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is missing from the dictionary, then that row was not found in the table (and require_all_keys must have been False).

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
```