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

