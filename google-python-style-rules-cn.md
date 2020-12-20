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
  * pylint的disable注释使用(如`# pylint: disable=invalid-name`)

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

#### 3.8.4 类
类应该具有文档字符串，文档字符串应该位于类定义的下一行，用来描述该类。如果类具有公共属性（Attributes），那么文档字符串应当有`Attributes`这一小节描述，并且和[函数的`Args`](https://google.github.io/styleguide/pyguide.html#doc-function-args)一节风格统一。

```Python
class SampleClass(object):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, likes_spam=False):
        """Inits SampleClass with blah."""
        self.likes_spam = likes_spam
        self.eggs = 0

    def public_method(self):
        """Performs operation blah."""
```

#### 3.8.5 块注释和行注释
最后要在代码中注释的地方是代码有技巧性的部分。如果你将要在下次[code review](http://en.wikipedia.org/wiki/Code_review)解释这段代码，那么你应该现在就给它写注释。对于复杂的操作，应该在其操作开始前写上若干行注释。对于不是一目了然的代码，应在其行尾添加注释。

```Python
# We use a weighted dictionary search to find out where i is in
# the array.  We extrapolate position based on the largest num
# in the array and the array size and then do binary search to
# get the exact number.

if i & (i-1) == 0:  # True if i is 0 or a power of 2.
```

为了提升可读性，行注释应该至少在代码2个空格后，并以`#`后接至少1个空格开始注释部分。

另外，绝对不要描述代码。假定阅读代码的人比你更精通Python（他只是不知道你试图做什么）。

```Python
# BAD COMMENT: Now go through the b array and make sure whenever i occurs
# the next element is i+1
```

#### 3.8.6 标点,拼写和语法
注意标点，拼写和语法，写得好的注释要比写得差的好读。

注释应当是和叙事性文本一样可读，并具有合适的大小写和标点。在许多情况下，完整的句子要比破碎的句子更可读。更简短的注释如行尾的注释可以不用太正式，但是你应该全篇保持风格一致。

尽管被代码审核人员指出在应该使用分号的地方使用了逗号是很令人沮丧的，将源代码维护在高度清楚可读的程度是很重要的。合适的标点，拼写和语法能够帮助达到这个目标。

### 3.9 类
类不需要显式的从`object`继承（除非为了与Python 2兼容）。

**Modern:**
```Python
class SampleClass:
    pass

class OuterClass:

    class InnerClass:
        pass
```

**Ancient:**
```Python
class SampleClass(object):
    pass

class OuterClass(object):

    class InnerClass(object):
        pass
```

### 3.10 字符串
使用`format`或`%`来格式化字符串，即使参数都是字符串对象。不过也不能一概而论, 你需要在`+`还是`%`（或是`format`）之间好好判定。

**Yes:**
```Python
x = a + b
x = '%s, %s!' % (imperative, expletive)
x = '{}, {}'.format(first, second)
x = 'name: %s; score: %d' % (name, n)
x = 'name: {}; score: {}'.format(name, n)
x = f'name: {name}; score: {n}'  # Python 3.6+
```

**No:**
```Python
x = '%s%s' % (a, b)  # use + in this case
x = '{}{}'.format(a, b)  # use + in this case
x = imperative + ', ' + expletive + '!'
x = 'name: ' + name + '; score: ' + str(n)
```

避免使用`+`和`+=`操作符来在循环内累加字符串。由于字符串是不可变的，这样做会创建不必要的临时对象，并且导致二次方而不是线性的运行时间。作为替代方案，你可以将每个子串加入列表，然后在循环结束后用`.join`连接列表（也可以将每个子串写入一个`io.BytesIO`缓存中）。

**Yes:**
```Python
items = ['<table>']
for last_name, first_name in employee_list:
    items.append('<tr><td>%s, %s</td></tr>' % (last_name, first_name))
items.append('</table>')
employee_table = ''.join(items)
```

**No:**
```Python
employee_table = '<table>'
for last_name, first_name in employee_list:
    employee_table += '<tr><td>%s, %s</td></tr>' % (last_name, first_name)
employee_table += '</table>'
```

在同一个文件（file）中，保持使用字符串引号的一致性。选择`'`或者`"`然后一以贯之。在字符串内可以使用另外一种引号，以避免在字符串中使用`\`转义符。

**Yes:**
```Python
Python('Why are you hiding your eyes?')
Gollum("I'm scared of lint errors.")
Narrator('"Good!" thought a happy Python reviewer.')
```

**No:**
```Python
Python("Why are you hiding your eyes?")
Gollum('The lint. It burns. It burns us.')
Gollum("Always the great lint. Watching. Watching.")
```

为多行字符串使用三重双引号`"""`而非三重单引号`'''`。当且仅当项目中使用单引号`'`来引用字符串时，才可能会使用三重`'''`为非文档字符串的多行字符串来标识引用。文档字符串必须使用三重双引号`"""`。

多行字符串不应随着代码其他部分缩进的调整而发生位置移动。如果需要避免在字符串中插入额外的空格，要么使用单行字符串连接或者带有[`textwarp.dedent()`](https://docs.python.org/3/library/textwrap.html#textwrap.dedent)的多行字符串来移除每行的起始空格。

**No:**
```Python
long_string = """This is pretty ugly.
Don't do this.
"""
```

**Yes:**
```Python
long_string = """This is fine if your use case can accept
    extraneous leading spaces."""

long_string = ("And this is fine if you can not accept\n" +
               "extraneous leading spaces.")

long_string = ("And this too is fine if you can not accept\n"
               "extraneous leading spaces.")

import textwrap

long_string = textwrap.dedent("""\
    This is also fine, because textwrap.dedent()
    will collapse common leading spaces in each line.""")
```

### 3.11 文件对象和socket
当使用结束后显式的关闭文件对象和socket。

除文件对象外，sockets或其他类似文件的对象在没有必要的情况下打开，会有许多缺点。例如：
* 他们可能会消耗有限的系统资源，例如文件描述符。如果在使用之后没有及时返还系统，处理很多这样对象的代码可能会将资源消耗殆尽。
* 保持一个文件的打开状态可能会阻止其他操作，诸如移动、删除之类的操作。
* 仅仅是从逻辑上关闭文件对象和sockets，那么它们仍然可能会被其共享的程序在无意中进行读或者写操作。只有当它们真正被关闭后，对于它们尝试进行读或者写操作将会抛出异常，并使得问题快速显现出来。

此外，尽管文件或socket在文件对象被销毁的同时被自动关闭，但是将文件对象的生命周期与文件状态进行绑定是糟糕的实践：

* 不能保证何时会真正将文件对象销毁。不同的Python解释器使用的内存管理技术不同，例如延时垃圾处理，可能会让对象的生命周期被无限期延长。
* 可能导致意料之外地对文件对象的引用，例如在全局变量或者异常回溯中，可能会让文件对象比预计的生命周期更长。

推荐使用[with语句](http://docs.python.org/reference/compound_stmts.html#the-with-statement)管理文件：
```Python
with open("hello.txt") as hello_file:
    for line in hello_file:
        print(line)
```

对于类似文件的对象，如果不支持with语句的可以使用`contextlib.closing()`：

```Python
import contextlib

with contextlib.closing(urllib.urlopen("http://www.python.org/")) as front_page:
    for line in front_page:
        print(line)
```

### 3.12  TODO注释
对于下述情况使用`TODO`注释：临时的，短期的解决方案或者足够好但是不完美的解决方案。

`TODO`注释以全部大写的字符串`TODO`开头，并带有写入括号内的姓名、e-mail地址或其他可以标识负责人或者包含关于问题最佳描述的issue。随后是这里未来应该做什么的说明。

有统一风格的`TODO`的目的是为了方便搜索并了解如何获取更多相关细节。写了`TODO`注释并不保证写的人会亲自解决问题。当你写了一个`TODO`，请注上你的名字。

```Python
# TODO(kl@gmail.com): Use a "*" here for string repetition.
# TODO(Zeke) Change this to use relations.
```

如果`TODO`注释形式为"未来某个时间点会做什么事"的格式，确保要么给出一个非常具体的时间点（例如"将于2009年11月前修复"）或者给出一个非常具体的事件（例如"当所有客户端都能够处理XML响应时就移除此代码"）。

### 3.13 import格式
imports应该在不同行，除了对于`typing`类的导入。例如：

**Yes:**
```Python
import os
import sys
from typing import Mapping, Sequence 
```

**No:**
```Python
import os, sys
```

import应集中放在文件顶部，在模块注释和文档字符串（docstrings）后面，模块globals和常量前面。应按照从最通用到最不通用的顺序排列分组：

1. Python未来版本import语句，例如：    
>   ```Python
>    from __future__ import absolute_import
>    from __future__ import division
>    from __future__ import print_function
>    ```

>    更多信息参看[上文](https://google.github.io/styleguide/pyguide.html#from-future-imports)

2. Python标准基础库import，例如：
>    ```Python
>    import sys
>    ```

3. 第三方库或包的import，例如：
>    ```Python
>    import tensorflow as tf
>    ```

4. 代码库内子包import，例如：
>    ```Python
>    from otherproject.ai import mind
>    ```
    
5. **此条已弃用**：和当前文件是同一顶级子包专用的import，例如：
>    ```Python
>    from myproject.backend.hgwells import time_machine
>    ```
>    在旧版本的谷歌Python代码风格指南中实际上是这样做的。但是现在不再需要了。**新的代码风格不再受此困扰**。简单的将专用的子包import和其他子包import同一对待即可。

在每个组内按照每个模块的完整包路径的字典序忽略大小写排序（即`from path import ...`当中的`path`）（译者注：即按照字母表排序）。可以根据情况在每个节之间增加空行。
```Python
import collections
import queue
import sys

from absl import app
from absl import flags
import bs4
import cryptography
import tensorflow as tf

from book.genres import scifi
from myproject.backend import huxley
from myproject.backend.hgwells import time_machine
from myproject.backend.state_machine import main_loop
from otherproject.ai import body
from otherproject.ai import mind
from otherproject.ai import soul

# Older style code may have these imports down here instead:
#from myproject.backend.hgwells import time_machine
#from myproject.backend.state_machine import main_loop 
```

### 3.14 语句（Statements）
一般来说，每行只有一条语句（statement）。

但是，如果测试结果与测试语句在一行放得下，你也可以将它们放在同一行。这种情况只有是`if`语句没有`else`时才能这样做，绝对不要对`try / except`这么做，因为`try`和`except`不能放在同一行。

**Yes:**
```Python
if foo: bar(foo)
```

**No:**
```Python
if foo: bar(foo)
else:   baz(foo)

try:               bar(foo)
except ValueError: baz(foo)

try:
    bar(foo)
except ValueError: baz(foo)
```

### 3.15 访问控制
在Python中，对于琐碎又不太重要的访问函数，你应该直接使用公有变量来取代它们，这样可以避免额外的函数调用开销。当添加更多功能时，你可以用`属性（property）`来保持语法的一致性. 

（译者注：重视封装的面向对象程序员看到这个可能会很反感，因为他们一直被教育：所有成员变量都必须是私有的！其实，那真的是有点麻烦啊。试着去接受Pythonic哲学吧！）

另一方面，如果访问更复杂，对于变量的访问开销显著，你应该使用像`get_foo()`和`set_foo()`这样的函数调用（参考[命名](https://google.github.io/styleguide/pyguide.html#s3.16-naming)指南）。如果过去的访问方式是通过属性（property），那么新访问函数不要绑定到property上。这样，任何试图通过老方法访问变量的代码就没法运行，使用者也就会意识到复杂性发生了变化。

### 3.16 命名
模块名命名范式：`module_name`，包名命名范式：`package_name`，类名命名范式：`ClassName`，方法名命名范式：`method_name`，异常名命名范式：`ExceptionName`，函数名命名范式：`function_name`，全局常量命名范式：`GLOBAL_CONSTANT_NAME`，全局变量命名范式：`global_var_name`，实例命名范式：`instance_var_name`，函数命名范式：`function_parameter_name`，局部变量命名范式`local_var_name`。

函数名、变量名、文件名应该是描述性的，避免缩写，尤其避免模糊或对读者不熟悉的缩写。并且不要通过删减单词内的字母来缩写。

#### 3.16.1 要避免的名字：
* 单字符名字，除非是以下特殊案例：
  * 计数器或者迭代器（例如`i, j, k, v`等等）。
  * 作为`try/except`中异常声明的`e`。
  * 作为`with`语句中文件对象的`f`。

    请注意不要滥用单字符命名。一般来说，变量名的描述程度应当与命名空间的范围成比例。例如对于变量`i`应该在5行代码块以内有效，如果对于多段嵌套代码含义则显得过于模糊。
* `-` 横线，不应出现在任何包名或模块名内。
* `__double_leading_and_trailing_underscore__` 首尾都双下划线的名字，这种名字是Python的内置保留名字。
* 有冒犯性质的名字（译者注：例如不文明词汇，侮辱性词汇）。

#### 3.16.2 命名约定
*  internal表示仅模块内可用、或者类内保护的或者私有的。
*  单下划线（`_`）开头表示该模块变量与方法是被保护的（linters会标记“被保护的成员变量”）（译者注：`from module import *`不会import）。双下划线（`__`也就是"dunder"）开头的实例变量或者方法表示类内私有（使用命名修饰）。我们不鼓励使用，因为这会对可读性和可测试性有影响，并且不会使得变量`真正`的私有。
*  将相关的类和顶级函数放在同一个模块里。不像Java，没必要限制一个类一个模块。
*  对类名使用大写字母开头的单词（如CapWords, 即Pascal风格），但是模块名应该用小写加下划线的方式（如lower_with_under.py）。尽管已经有很多现存的模块使用类似于CapWords.py这样的命名，但现在已经不鼓励这样做，因为如果模块名碰巧和类名一致，这会让人困扰（例如：我刚刚写的是`import StringIO`还是`from StringIO import StringIO`？）。
*  在*unittest*方法中可能是`test`开头来分割名字的组成部分，即使这些组成部分是使用大写字母驼峰式的。典型的可能模式像：`test<MethodUnderTest>_<state>`，例如`testPop_EmptyStack`是可以的。对于测试方法的命名没有明确的正确方法。

#### 3.16.3 文件（File）命名
Python文件拓展名必须为`.py`，不可以包含`-`（中划线）。这保证了能够被正常import和单元测试。如果希望一个可执行文件不需要拓展名就可以被调用，那么建立一个软连接或者一个简单的bash打包脚本包括`exec "$0.py" "$@"`。

#### 3.16.4 Guido的指导建议
| **类型** | **公共** | **内部** |
| --- | --- | --- |
| 包 | `lower_with_under` |  |
| 模块 | `lower_with_under` | `_lower_with_under` |
| 类 | `CapWords` | `_CapWords` |
| 异常 | `CapWords` |  |
| 函数 | `lower_with_under()` | `_lower_with_under()` |
| 全局/类常量 | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| 全局/类变量 | `lower_with_under` | `_lower_with_under` |
| 实例变量 | `lower_with_under` | `_lower_with_under`(受保护) |
| 方法名 | `lower_with_under()` | `_lower_with_under()`(受保护) |
| 函数/方法参数 | `lower_with_under` |  |
| 局部变量 | `lower_with_under` |  |

### 3.17 Main
在Python当中，`pydoc`与单元测试都要求模块（Module）是可导入的（importable）。如果一个文件注定被当做可执行文件来运行，那么他的主函数应该在`main()`函数内，并且你的代码在执行之前，应该总是检查`if __name__ == "__main__"`，这样你的代码就不会在被导入的时候运行。

若使用[absl](https://github.com/abseil/abseil-py)，请使用`app.run`：

```Python
from absl import app
...

def main(argv):
    # process non-flag arguments
    ...

if __name__ == '__main__':
    app.run(main)
```
否则使用：
```Python
def main():
    ...

if __name__ == '__main__':
    main()
```

所有顶级代码在模块被导入的时候，都会被执行。应当注意当使用`pydoc`形成文档的时候，不要去调用函数、创建对象或者执行那些不应该被执行的操作。

### 3.18 函数长度
优先写小而专一的函数。

长函数有时候是合适的，故而函数长度没有硬性的限制。但是如果一个函数超过40行的时候，就要考虑是否要在不影响程序结构的前提下分解函数。保持函数的简短与简洁，这样有利于其他人读懂和修改代码。

在处理一些代码时，可能会发现有些函数很长而且复杂。不要畏惧调整现有代码，如果调整这样的函数非常困难，如难以对报错debug或者希望在几个不同的上下文中使用它的部分代码，那么请考虑将函数拆解成若干个更小更可控的片段。

### 3.19 类型注释

#### 3.19.1 基本规则
* 请熟悉[PEP-484](https://www.python.org/dev/peps/pep-0484/)。
* 在方法中，只在必要时给`self`或者`cls`增加合适的类型信息。例如`@classmethod def create(cls: Type[T]) -> T: return cls()`。
* 如果其他变量或返回类型不定，使用`Any`。
* 无需注释模块中的所有函数。
    * 至少需要注明公共接口（public APIs）。
    * 使用类型检查来在安全性和声明清晰性以及灵活性之间平衡。
    * 标注容易因类型相关而抛出异常的代码（previous bugs or complexity，此处译者认为是与上一条一致，平衡安全性和复杂性）。
    * 标注难理解的代码。
    * 若代码中的类型已经稳定，可以进行注释。对于一份成熟的代码，多数情况下，即使注释了所有的函数，也不会丧失太多的灵活性。

#### 3.19.2 换行
尽量遵守既定的[缩进规则](https://google.github.io/styleguide/pyguide.html#indentation)。

注释后，很多函数签名将会变成每行一个参数：
```Python
def my_method(self,
              first_var: int,
              second_var: Foo,
              third_var: Optional[Bar]) -> int:
  ...
```

优先在变量之间换行，而非其他地方如变量名和类型注释之间。如果都能放在一行内，就放在一行。
```Python
def my_method(self, first_var: int) -> int:
  ...
```

