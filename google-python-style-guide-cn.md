## 1 背景
================================

Python 是 Google主要的脚本语言。这本风格指南主要包含的是针对python的编程准则。

为帮助读者能够将代码准确格式化，我们提供了针对[Vim的配置文件](https://google.github.io/styleguide/google_python_style.vim)。对于Emacs用户，保持默认设置即可。许多团队使用[yapf](https://github.com/google/yapf/)作为自动格式化工具以避免格式不一致。

## 2 Python语言规范
================================

### 2.1 Lint
使用该[pylintrc](https://google.github.io/styleguide/pylintrc)对你的代码运行`pylint`。

#### 2.1.1 定义:
`pylint`是一个在Python源代码中查找bug的工具。对于C和C++这样的不那么动态的（译者注: 原文是less dynamic）语言，这些bug通常由编译器来捕获。由于Python的动态特性，有些警告可能不对。不过伪告警应该相对较少。

#### 2.1.2 优点:
可以捕获容易忽视的错误，例如输入错误，使用未赋值的变量等。

#### 2.1.3 缺点:
`pylint`不完美。要利用其优势，我们有时侯需要：a) 围绕着它来写代码 b) 抑制其告警 c) 改进它 或者d) 忽略它。

#### 2.1.4 结论
确保对代码应用`pylint`。

抑制不准确的警告，以便能够将其他警告暴露出来。你可以通过设置一个行级别的注释来抑制警告。例如:
```Python
dict = 'something awful'  # Bad Idea... pylint: disable=redefined-builtin
```
`pylint`警告是以符号名(如`empty-docstring`)来标识的。google特定的警告则是以`g-`开头。如果警告的符号名不够见名知意，那么请对其增加一个详细解释。采用这种抑制方式的好处是我们可以轻松查找抑制并回顾它们。

你可以使用命令`pylint --list-msgs`来获取pylint告警列表。你可以使用命令 `pylint --help-msg=C6409`，以获取关于特定消息的更多信息。

相比较于之前使用的`pylint: disable-msg`，本文推荐使用`pylint: disable`。

在函数体中`del`未使用的变量可以消除参数未使用告警。总是记得要加一条注释说明你为何`del`它们，注释使用"Unused"就可以，例如：
```Python
def viking_cafe_order(spam, beans, eggs=None):
    del beans, eggs  # Unused by vikings.
    return spam + spam + spa
```
其他消除这个告警的方法还有使用`_`标识未使用参数，或者给这些参数名加上前缀 `unused_`，或者直接把它们赋值给`_`。这些方法都是允许的，但是已经不再被鼓励使用。前两种方式会影响到通过参数名传参的调用方式，而最后一种并不能保证参数确实未被使用。

--------------------
### 2.2 Imports
只在import包和模块的时候使用`import`，而不要用来import单独的类或函数。(这一条对于[typing_module](https://google.github.io/styleguide/pyguide.html#typing-imports)模块的imports例外)

#### 2.2.1 定义：
一个模块到另一个模块之间共享代码的复用性机制。

#### 2.2.2 Pros：
命名空间管理约定简单，每个标识符的源都以一种一致的方式指明。例如`x.Obj`表示`Obj`是在模块`x`中定义的。

#### 2.2.3 Cons：
一方面，模块名可能会有冲突；另一方面，一些模块名可能很长，不太方便。

#### 2.2.4 结论：
* `import x`（当`x`是包或模块）
* `from x import y`（当`x`是包前缀，`y`是不带前缀的模块名）
* `from x import  y as z`（如果两个要导入的模块都叫做`y`或者`y`太长了不利于引用的时候）
* `import y as z`（仅在当`z`是通用的缩写的时候使用，例如`import numpy as np`）

例如，模块`sound.effects.echo`可以用如下方式导入：
```Python
from sound.effects import echo
...
echo.EchoFilter(input, output, delay=0.7, atten=4)
```
导入时不要使用相对名称。即使模块在同一个包中，也要使用完整包名。这能帮助你避免无意间导入一个包两次。

从[typing module](https://google.github.io/styleguide/pyguide.html#typing-imports)和[six.moves module](https://six.readthedocs.io/#module-six.moves)进行import不适用上述规则。

--------------------
### 2.3 包
使用模块的全路径名来import包(Package)中的每个模块。

#### 2.3.1 Pros
能够避免模块名冲突以及由于模块搜索路径与作者预期不符而造成的错误引用。让查找模块更简单。

#### 2.3.2 Cons
让部署代码时有些困难，因为你必须复制包的层次结构。不过对于现在的部署机制而言，这其实不是问题。

#### 2.3.3 结论
所有的新代码都应该用完整包名来import每个模块。

import示例应该像这样：

**Yes:**
```Python
# Reference absl.flags in code with the complete name (verbose).
# 在代码中使用完整路径调用absl.flags
import absl.flags
from doctor.who import jodie

FLAGS = absl.flags.FLAGS
```
``` Python
# Reference flags in code with just the module name (common).
# 在代码中只用模块名来调用flags
from absl import flags
from doctor.who import jodie

FLAGS = flags.FLAGS
```

**No:**（假设文件在`doctor/who`中，并且`jodie.py`也在该路径下）
```Python
# Unclear what module the author wanted and what will be imported. The actual
# import behavior depends on external factors controlling sys.path.
# Which possible jodie module did the author intend to import?
# 不清楚作者想要哪个模块以及最终import的是哪个模块,
# 实际的import操作依赖于受到外部参数控制的sys.path
# 那么哪一个可能的jodie模块是作者希望import的呢?
import jodie
```
不应假定主入口脚本所在的目录就在`sys.path`中，虽然这种情况在一些环境下是存在的。当主入口脚本所在目录不在`sys.path`中时，代码将假设`import jodie`是导入的一个第三方库或者是一个名为`jodie`的顶层包，而不是本地的`jodie.py`。

--------------------
### 2.4 异常
异常处理是允许被使用的，但使用时务必谨慎。

#### 2.4.1 定义
异常是一种从正常代码段控制流中跳出以处理错误或者其他异常条件的手段。

#### 2.4.2 Pros
正常代码的控制流时不会被错误处理代码影响的。异常处理同样允许在某些情况下，控制流跳过多段代码，例如在某一步从N个嵌入函数返回结果而非继续执行错误代码。

#### 2.4.3 Cons
可能会导致让人困惑的控制流。调用库时容易忽略错误情况。 

#### 2.4.4 结论
异常必定遵循特定条件：
* 优先合理的使用内置异常类。比如`ValueError`指示了一个类似于这样的程序错误：在方法需要正数的情况下传递了一个负数的错误。不要使用`assert`语句来验证对外的API的参数值的正确性。`assert`是用来保证内部正确性的，它既不是用来强制纠正参数使用，也不是用来指示内部某些意外事件发生的情况。若需要使用异常来指示前述后者的情况，不要用 `assert`，用`raise`语句，例如:

**Yes:**
``` Python
def connect_to_next_port(self, minimum):
    """Connects to the next available port.

    Args:
        minimum: A port value greater or equal to 1024.

    Returns:
        The new minimum port.

    Raises:
        ConnectionError: If no available port is found.
    """
    if minimum < 1024:
        # Note that this raising of ValueError is not mentioned in the doc
        # string's "Raises:" section because it is not appropriate to
        # guarantee this specific behavioral reaction to API misuse.
        raise ValueError(f'Min. port must be at least 1024, not {minimum}.')
    port = self._find_next_open_port(minimum)
    if not port:
        raise ConnectionError(
            f'Could not connect to service on port {minimum} or higher.')
    assert port >= minimum, (
        f'Unexpected port {port} when minimum was {minimum}.')
    return port
```

**No:**
```Python
def connect_to_next_port(self, minimum):
    """Connects to the next available port.

    Args:
    minimum: A port value greater or equal to 1024.

    Returns:
    The new minimum port.
    """
    assert minimum >= 1024, 'Minimum port must be at least 1024.'
    port = self._find_next_open_port(minimum)
    assert port is not None
    return port
```
* 模块或包也许会定义它们自己的异常类。当有这种情况的时候，这些异常基类应当从内建的Exception类继承。并且模块的异常基类后缀应该叫做`Error`。
* 永远不要使用`except:`语句来捕获所有异常，也不要捕获`Exception`或者 `StandardError`，除非：
  * 你打算重新触发该异常
  * 你已经在当前线程的最外层（记得还是要打印一条错误消息）。

  在异常这方面，Python非常宽容，`except:`真的会捕获包括变量名拼写错误、调用`sys.exit()`、`Ctrl+C`中断、单元测试失败在内的任何你都不想捕获的错误。使用`except:`很容易隐藏真正的bug。

* 尽量减少`try/except`块中的代码量。`try`块的体积越大，就越容易出现期望之外的异常被捕获的现象。这种情况下，`try/except`块将隐藏真正的错误。
* 使用`finally`子句来执行那些无论`try`块中有没有异常都应该被执行的代码。这对于清理资源常常很有用，例如关闭文件。

--------------------
### 2.5 全局变量
避免使用全局变量。

#### 2.5.1 定义
在模块级别或者作为类属性声明的变量。

#### 2.5.2 Pros
有些时候有用。

#### 2.5.3 Cons
在import的过程中，有可能改变模块行为，因为在模块首次被引入的过程中，全局变量就已经被声明。

#### 2.5.4 结论
避免全局变量。但是鼓励使用模块级的常量，例如`MAX_HOLY_HANDGRENADE_COUNT = 3`。注意常量命名必须全部大写，并用`_`分隔。具体参见[命名规则](https://google.github.io/styleguide/pyguide.html#s3.16-naming)。

------------------------
### 2.6 嵌套/局部/内部类和函数
使用内部类或者嵌套函数可以用来覆盖某些局部变量。

#### 2.6.1 定义
类能够被定义在方法，函数或者类中。函数也能够被定义在方法或函数中。内嵌函数对于封闭作用域中的变量只有可读的权限。（译者注：即内嵌函数可以读外部函数中定义的变量，但是无法改写，除非使用`nonlocal`或者`global`提前进行声明）

#### 2.6.2 Pros
允许定义仅用于有效范围的工具类和函数，在装饰器中比较常用。 

#### 2.6.3 Cons
嵌套类或局部类的实例不能序列化（pickled）。内嵌的函数和类无法直接测试，同时内嵌函数和类会使外部函数的可读性变差。

#### 2.6.4 结论
可以使用内部类或者内嵌函数，但是应当注意一些问题。应该避免使用内嵌函数或类，除非是想覆盖某些值。若想对模块的用户隐藏某个函数，不要采用嵌套它来隐藏，应该在需要被隐藏的方法的模块级名称加`_`前缀，这样它依然是可以被测试的。

------------------------
### 2.7 列表推导和生成器表达式
在简单情况下是可用的。

#### 2.7.1 定义
列表，字典和集合的推导式与生成器（generator）表达式提供了一种简洁高效的方式来创建容器和迭代器（iterators），而不必借助`map()`，`filter()`，或者`lambda`。（译者注: 元组是没有推导式的，`()`内加类似推导式的句式返回的是个生成器）

#### 2.7.2 Pros
简单的推导表达式创建方式比其他的字典，列表或集合创建方法更加简明清晰。生成器表达式能有很高的效率，因为它避免了一次性生成整个列表。

#### 2.7.3 Cons
复杂的列表推导或者生成器表达式可能难以阅读。

#### 2.7.4 结论
列表推导和生成器表达式适用于简单情况。每个部分应该单独置于一行，包括：映射表达式，`for`语句，过滤器表达式。禁止多重`for`语句或过滤器表达式。复杂情况下还是应该使用循环。

**Yes:**
```Python
result = [mapping_expr for value in iterable if filter_expr]

result = [{'key': value} for value in iterable
          if a_long_filter_expression(value)]

result = [complicated_transform(x)
          for x in iterable if predicate(x)]

descriptive_name = [
    transform({'key': key, 'value': value}, color='black')
    for key, value in generate_iterable(some_input)
    if complicated_condition_is_met(key, value)
]

result = []
for x in range(10):
    for y in range(5):
        if x * y > 10:
            result.append((x, y))

return {x: complicated_transform(x)
        for x in long_generator_function(parameter)
        if x is not None}

squares_generator = (x**2 for x in range(10))

unique_names = {user.name for user in users if user is not None}

eat(jelly_bean for jelly_bean in jelly_beans
    if jelly_bean.color == 'black')
```

**No:**
```Python
result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]

return ((x, y, z)
        for x in xrange(5)
        for y in xrange(5)
        if x != y
        for z in xrange(5)
        if y != z)
```

------------------------
### 2.8 默认迭代操作符和操作符
如果类型支持，就使用默认迭代操作符（iterators）和操作符（operators）。比如列表，字典及文件对象等。（译者注：此处的iterators应当被翻译为迭代操作符，与后续关系操作符对应，例如`for`语句用来迭代容器对象）

#### 2.8.1 定义
容器类型，例如字典和列表，定义了默认的迭代操作符和关系测试操作符（`in`和`not in`）。

#### 2.8.2 Pros
默认操作符和迭代器简单且高效。它们直接表达了操作的含义，没有额外的方法调用。使用默认操作符的函数是通用的。它可以用于支持该操作的任何类型。

#### 2.8.3 Cons
你没法通过阅读方法名来区分对象的类型（例如，`has_key()`意味着字典）。不过这也是优点。

#### 2.8.4 结论
如果类型支持，就使用默认迭代操作符和操作符，例如列表，字典和文件。内建类型也定义了迭代器方法。优先考虑这些方法，而不是那些返回列表的方法。当然，这样遍历容器时，你将不能修改容器。除非必要，否则不要使用诸如`dict.iter*()`这类python2的特定迭代方法。

**Yes:**
```Python
for key in adict: ...
if key not in adict: ...
if obj in alist: ...
for line in afile: ...
for k, v in dict.iteritems(): ...
```

**No:**
```Python
for key in adict.keys(): ...
if not adict.has_key(key): ...
for line in afile.readlines(): ...
```

------------------------
### 2.9 生成器
按需使用生成器。

#### 2.9.1 定义
生成器函数返回一个迭代器，并且每次执行`yield`语句的时候生成一个值。在生成一个值之后，生成器函数的运行状态被挂起，直到下一次生成。

#### 2.9.2 Pros
简化代码，因为每次调用时局部变量和控制流的状态都会被保存。比起一次创建一系列值的函数，生成器占用的内存更少。

#### 2.9.3 Cons
没有。

#### 2.9.4 结论
鼓励使用。注意在生成器函数的文档字符串中使用`Yields:`而不是`Returns:`。

------------------------
### 2.10 Lambda函数
适用于单行函数。

#### 2.10.1 定义:
与声明式函数相反，Lambda函数在表达式中定义匿名函数。常用于为`map()`和`filter()`之类的高阶函数定义回调函数或者操作符。

#### 2.10.2 优点:
方便。

#### 2.10.3 缺点:
比局部函数更难读懂和debug，匿名性意味着堆栈跟踪更难懂。表达性受限因为lambda函数只包含一个表达式。

#### 2.10.4 结论:
适用于单行函数。如果代码超过60-80个字符，最好还是定义成常规（嵌套）函数。

对于常见的操作符，例如乘法操作符，使用`operator`模块中的函数以代替lambda函数。例如，推荐使用`operator.mul`，而不是`lambda x, y: x * y`。 

------------------------
### 2.11 条件表达式
简单情况下可以使用。

#### 2.11.1 定义
条件表达式（又名三元运算符）是对于if语句的一种更为简短的句法规则。例如：`x = 1 if cond else 2`。

#### 2.11.2 Pros
比if语句更加简短和方便。

#### 2.11.3 Cons
比if语句难于阅读。如果if表达式很长，有时会难以定位条件位置。

#### 2.11.4 结论：
简单情况可以使用。条件表达式的每一个部分都必须在一行内完成（包括真值表达式，if表达式，else表达式）。当处理的情况比较复杂时，使用完整的if语句。

**Yes:**
```Python
one_line = 'yes' if predicate(value) else 'no'
slightly_split = ('yes' if predicate(value)
                  else 'no, nein, nyet')
the_longest_ternary_style_that_can_be_done = (
    'yes, true, affirmative, confirmed, correct'
    if predicate(value)
    else 'no, false, negative, nay')
```

**No:**
```Python
bad_line_breaking = ('yes' if predicate(value) else
                     'no')
portion_too_long = ('yes'
                    if some_long_module.some_long_predicate_function(
                        really_long_variable_name)
                    else 'no, false, negative, nay')
```

### 2.12 默认参数值
大多数情况下都OK。

#### 2.12.1 定义
你可以在函数参数列表的最后指定变量的值，例如，`def foo(a, b = 0):`。如果调用`foo`时只带一个参数，则b被设为0。如果带两个参数，则b的值等于第二个参数。

#### 2.12.2 Pros
 经常有一些函数使用了大量的默认参数，但很少你会有修改这些默认值的情况。默认参数值提供了一种简单的方法来完成这件事，你不需要为这些罕见的例外定义大量函数。同时, Python也不支持重载方法和函数。默认参数是一种“仿造”重载行为的简单方式。

#### 2.12.3 Cons
默认参数只在模块加载时进行一次求值。如果参数是列表或字典之类的可变类型，这就会出现问题，如果函数修改了默认参数的对象（例如向列表执行`append`操作）, 默认值就被修改了。

#### 2.12.4 结论：
鼓励使用, 不过有如下注意事项：

不要在函数或方法定义中使用可变对象作为参数的默认值。

**Yes:**
```Python
Yes: def foo(a, b=None):
         if b is None:
             b = []
Yes: def foo(a, b: Optional[Sequence] = None):
         if b is None:
             b = []
Yes: def foo(a, b: Sequence = ()):  # Empty tuple OK since tuples are immutable
```

**No:**
```Python
No:  def foo(a, b=[]):
     ...
No:  def foo(a, b=time.time()):  # The time the module was loaded???
     ...
No:  def foo(a, b=FLAGS.my_thing):  # sys.argv has not yet been parsed...
     ...
No:  def foo(a, b: Mapping = {}):  # Could still get passed to unchecked code
    ...
```

--------------------
### 2.13 特性（properties）
（译者注：参照fluent python，这里将"property"译为"特性"，而"attribute"译为属性。python中数据的属性和处理数据的方法统称**属性（arrtibute）**，而在不改变类接口的前提下用来修改数据属性的存取方法我们称为**特性（property）**。）

使用属性可以通过简单而轻量级的访问器（getter）和设定器（setter）方法来访问或设定数据。

#### 2.13.1 定义
一种装饰器方法，在计算比较轻量级的时候，作为标准的属性访问方法来获取和设定一个属性的方式。

#### 2.13.2 Pros
通过消除对于简单属性访问的显式的get和set方法调用，来提升代码的可读性。允许惰性计算（译者注：应当指yield语句）。使用Pythonic的方式来维护类的接口。就性能而言，当直接访问变量是合理的，添加访问方法就显得琐碎而无意义。使用特性（properties）可以绕过这个问题，将来也可以在不破坏接口的情况下将访问方法加上（译者注：为变量添加装饰器@propetry后，仍然可以构建一个访问方法来返回该变量的值而不破坏整体接口的构造）。

#### 2.13.3 Cons
在Python2中必须继承自`object`类。可能隐藏比如操作符重载之类的副作用。继承时，对于子类而言可能会让人困惑。（译者注：这里没有修改原始翻译，其实就是`@property`装饰器是不会被继承的）

#### 2.13.4 结论：
在你的新代码中，对于你会使用和轻量级的访问与设定方法的地方，使用属性来进行访问与设定数据。属性应当使用`@property`[装饰器](https://google.github.io/styleguide/pyguide.html#s2.17-function-and-method-decorators)来进行创建。

如果子类没有覆盖属性，那么属性的继承可能看上去不明显。因此使用者必须确保访问方法间接被调用，以保证子类中的重载方法被属性调用（使用模板方法设计模式）。

**Yes:**
```Python
class Square(object):
    """A square with two properties: a writable area and a read-only perimeter.

    To use:
    >>> sq = Square(3)
    >>> sq.area
    9
    >>> sq.perimeter
    12
    >>> sq.area = 16
    >>> sq.side
    4
    >>> sq.perimeter
    16
    """

    def __init__(self, side):
        self.side = side

    @property
    def area(self):
        """Area of the square."""
        return self._get_area()

    @area.setter
    def area(self, area):
        return self._set_area(area)

    def _get_area(self):
        """Indirect accessor to calculate the 'area' property."""
        return self.side ** 2

    def _set_area(self, area):
        """Indirect setter to set the 'area' property."""
        self.side = math.sqrt(area)

    @property
    def perimeter(self):
        return self.side * 4
```

--------------------
### 2.14 True/False表达式求值
尽可能使用“隐式”的false。

#### 2.14.1 定义
Python在布尔上下文中会将某些特定值求值为false。一条快速的“经验原则”是, 所有的“空”值都被认为是false。因此0，None，[]，{}，""都被认为是false。

#### 2.14.2 Pros
使用Python布尔类型的条件语句可读性更好而且更难出错，大多数情况下，这种方式也更高效。

#### 2.14.3 Cons
对于C/C++开发者而言可能有些奇怪。

#### 2.14.4 结论：
如果可能的话，使用“隐式”的False。例如使用`if foo:`，而非`if foo != []:`。下面列举了一些你应该牢记的注意事项：
* 总是使用`if foo is None:`（或者`is not None`）来检测`None`值。例如，当测试一个变量或者参数默认值是否由`None`被设置为其他值。这个值在布尔语义下可能是false！（译者注：`is`比较的是对象的id()，这个函数返回的通常是对象的内存地址，考虑到CPython的对象重用机制，可能会出现生命周不重叠的两个对象会有相同的id）
* 永远不要用`==`将一个布尔变量与`False`相比较。反之应当使用`if not x:`替代。如果你需要区分`False`与`None`，那么你应该用`if not x and x is not None`。
* 对于序列类型（字符串，列表，元组），使用空序列是false的原则。因此，`if seq:`与`if not seq:`分别比`if len(seq):`与`if not len(seq):`更好。
* 当处理整数时，“隐式”的false相比较优势而言也许会带来更大的风险（也就是说，一不小心将`None`和0进行了相同的处理）。你可以将一个已知是整型（且不是len()的返回结果）的值与0比较。

**Yes:**
```Python
if not users:
    print('no users')

if foo == 0:
    self.handle_zero()

if i % 10 == 0:
    self.handle_multiple_of_ten()

def f(x=None):
    if x is None:
        x = []
```

**No:**
```Python
if len(users) == 0:
    print('no users')

if foo is not None and not foo:
    self.handle_zero()

if not i % 10:
    self.handle_multiple_of_ten()

def f(x=None):
    x = x or []
```
* 注意`'0'`（即`0`字符串）会被当做true。

--------------------
### 2.15 过时的语言特性
尽可能利用字符串方法替代字符串模块（`string`模块）。使用函数调用语法取代`apply`。使用列表推导与`for`循环替代`filter`与`map`当函数的参数大概率是一个行内lambda表达式的时候（译者注：使用[lambda x: x+2 for x in seq]而不是map(lambda x: x+2, seq)）。用`for`循环替代`reduce`。

#### 2.15.1 Pros
当前Python版本提供了人们普遍更倾向的构建方式。

#### 2.15.2 Cons
我们不使用任何不支持这些特性的Python版本，因而没有理由不使用新方式。

**Yes:**
```Python
words = foo.split(':')

[x[1] for x in my_list if x[2] == 5]

map(math.sqrt, data)  # Ok. No inlined lambda expression.

fn(*args, **kwargs)
```

**No:**
```Python
words = string.split(foo, ':')

map(lambda x: x[1], filter(lambda x: x[2] == 5, my_list))

apply(fn, args, kwargs)
```

--------------------
### 2.16 词法作用域（Lexical Scoping）
可以使用。

#### 2.16.1 定义
一个内嵌Python函数可以引用在闭包命名空间内定义的变量，但是不能对其赋值。变量绑定的解析基于的是词法作用域，即基于静态程序文本。任何对块内某个变量的赋值都会导致Python将所有对该名称的引用当做局部变量，即使使用先于赋值操作。如果有全局声明，那么改名称就会被认为是全局变量。

一个使用这个特性的例子是：
```Python
def get_adder(summand1):
    """Returns a function that adds numbers to a given number."""
    def adder(summand2):
        return summand1 + summand2

    return adder
```

#### 2.16.2 Pros
通常可以带来更清晰、优雅的代码。尤其会让有经验的Lisp和Scheme（以及Haskell和ML还有其他）的程序员感到欣慰。

#### 2.16.3 Cons
可能会导致令人迷惑的bug。例如这个基于[PEP-0227](http://www.google.com/url?sa=D&q=http://www.python.org/dev/peps/pep-0227/)的例子.

```Python
i = 4
def foo(x):
    def bar():
        print(i, end='')
    # ...
    # A bunch of code here
    # ...
    for i in x:  # Ah, i *is* local to foo, so this is what bar sees
        print(i, end='')
    bar()
```
所以`foo([1, 2, 3])`会打印`1 2 3 3`而非`1 2 3 4`。

#### 2.16.4 建议
可以使用

--------------------
### 2.17 函数和方法装饰器
在明显有好处时，谨慎明智的使用装饰器。避免使用`@staticmethod`，控制使用`@classmethod`。

### 2.17.1 定义
[函数和方法装饰器](https://docs.python.org/3/glossary.html#term-decorator)（也就是`@`记号）。最常见的装饰器是`@property`，用来将常规方法转换为动态可计算的属性。但是，装饰器语法也允许用户定义装饰器。特别地，对于一些函数，例如`my_function`：
```Python
class C(object):
    @my_decorator
    def method(self):
        # method body ...
```
等效于
```Python
class C(object):
    def method(self):
        # method body ...
    method = my_decorator(method)
```

#### 2.17.2 Pros
能够优雅的对方法进行某种转换，并且该转换可能减少一些重复代码，并强化不变性等等。

#### 2.17.3 Cons
装饰器可以在函数的参数或返回值上执行任何操作，这可能导致出人意料的隐藏操作行为。此外，装饰器在import的时候就被执行。从装饰器代码中捕获错误并处理是很困难的。

#### 2.17.4 结论：
如果好处很明显，就明智而谨慎的使用装饰器。装饰器应该遵守和函数一样的导入和命名规则。装饰器的python文档应该清晰的说明该函数是一个装饰器。请为装饰器编写单元测试。 

避免装饰器自身对外界的依赖（即不要依赖于文件，socket，数据库连接等），因为装饰器运行时这些资源可能不可用（由`pydoc`或其它工具导入）。应该保证一个用有效参数调用的装饰器在所有情况下都是成功的。

装饰器是一种特殊形式的“顶级代码”，参考后面关于[main](https://google.github.io/styleguide/pyguide.html#s3.17-main)的话题。

除非是为了将方法和现有的API集成，否则不要使用`staticmethod`。多数情况下，将方法封装成模块级的函数可以达到同样的效果。谨慎使用`classmethod`。通常只在定义备选构造函数，或者写用于修改诸如进程级缓存等必要的全局状态的特定类方法才用。

--------------------
### 2.18 线程
不要依赖于内建类型的原子性。

尽管Python内置数据类型例如字典等似乎有原子性操作，仍有一些罕见情况下，他们是非原子的（比如,如果`__hash__`或者`__eq__`被实现为Python方法），就不应该依赖于这些类型的原子性。也不应该依赖于原子变量赋值（因为这依赖于字典）。

优先使用Queue模块的`Queue`类来作为线程之间通讯数据的方式。此外，要是用threading模块和其locking primitives（锁原语）。了解条件变量的合理用法以便于使用`threading.Condition`而非使用更低级的锁。

--------------------
### 2.19 威力过大的特性
尽量避免使用。

#### 2.19.1 定义
Python是一种非常灵活的语言，并且提供了很多花哨的特性，诸如定制元类（custom metaclasses），访问字节码（access to bytecode），动态编译（on-the-fly compilation），动态继承（dynamic inheritance），对象父类重定义（object reparenting），import hacks，反射（reflection）（例如一些对于`getattr()`的应用），系统内置的修改（modification of system internals）等等。

#### 2.19.2 Pros
这些是非常强大的语言特性。可以让程序更紧凑。

#### 2.19.3 Cons
在你的代码中避免这些特性。

当然，利用了这些特性的来编写的一些标准库是值得去使用的，比如`abc.ABCMeta`，`collection.namedtuple`，`dataclasses`，`enum`等。

--------------------
### 2.20 新版本Python：Python3和从 `__future__` import
Python 3已经发布了！虽然不是每一个项目都已经准备好使用Python 3了，但是所有代码应该以Python 3兼容的方式进行编写（并且尽量在Python 3的环境下进行测试）。

#### 2.20.1 定义
python 3是python语言的一个重大改进版本，虽然已有大量代码是python 2.7写的，但是通过一些简单的调整就可以使得代码的表意更加简明，因此最好为了在Python 3环境下进行运行做准备。

#### 2.20.2 Pros
一旦项目依赖都就绪，那么使用python 3写的代码更加清晰并且方便运行。

#### 2.20.3 Cons
导入一些看上去实际用不到的模块到代码里显得有些奇怪。

#### 2.20.4 结论：

**from __future__ imports**

鼓励使用`from __future__ import`语句。所有新代码都应该包含下述代码，而现有代码应该被更新以尽可能兼容：
```Python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
```
如果你不太熟悉这些,详细阅读这些：[绝对import](https://www.python.org/dev/peps/pep-0328/)，[新的`/`除法行为](https://www.python.org/dev/peps/pep-0238/)，和[`print`函数](https://www.python.org/dev/peps/pep-3105/)

除非代码是只在Python 3下运行，否则不要忽略或者移除以上的导入，即使他们在这个模块中没有用。最好在所有文件里都保留这样的导入，这样若有人用到了这些特性时，后续编辑时不会忘记导入。
    
还有其他的一些来自`from __future__`的语句。请在你认为合适的地方使用它们。本文没有推荐`unicode_literals`，因为我们认为它不是很棒的改进，它在Python 2.7中大量引入例隐式的默认编码转换。大多数情况下还是推荐显式的使用`b`和`u`以及unicode字符串来显式的指示编码转换。

**The six, future, or past libraries**

当项目需要支持Python 2和3时，根据需求使用[six](https://pypi.org/project/six/),[future](https://pypi.org/project/future/)和[past](https://pypi.org/project/past/)。这些库可以使代码更加清晰和简单。

--------------------
### 2.21 代码类型注释
可以根据[PEP-484](https://www.python.org/dev/peps/pep-0484/)对Python 3代码进行类型注释，并且在build时用类型检查工具例如[pytype](https://github.com/google/pytype)进行类型检查。

类型注释可以在源码中或在[stub pyi file](https://www.python.org/dev/peps/pep-0484/#stub-files)中。只要可能，注释就应写在源代码中。对于第三方模块或拓展模块使用pyi文件。

#### 2.21.1 定义
类型注释（也称为“类型提示”）是用于函数或方法参数和返回值的：
```Python
def func(a: int) -> List[int]:
```
也可以使用[PEP-526](https://www.python.org/dev/peps/pep-0526/)中的语法来声明变量类型:
```Python
a: SomeType = some_func()
```
在必须支持老版本Python运行的代码中则可以这样注释：
```Python
a = some_func()  #type: SomeType
```

#### 2.21.2 Pros
类型注释提升代码的可读性和可维护性。类型检查会将很多运行错误转化为构建错误，也减少了使用[过于强力特性](https://google.github.io/styleguide/pyguide.html#power-features)的能力。

#### 2.21.3 Cons
需要不断更新类型声明，对于自认为正确的代码可能会报类型错误，使用[类型检查](https://github.com/google/pytype)可能减少使用[过于强力特性](https://google.github.io/styleguide/pyguide.html#power-features)的能力。

#### 2.21.4 建议
强烈鼓励在更新代码的时候进行Python类型分析。在对公共API进行补充和修改时，包括Python类型声明并通过构建系统中的Pytype进行检查。对Python来说静态类型检查比较新，我们承认，一些意料外的副作用（例如错误推断的类型）可能拒绝一些项目的使用。这种情况下，鼓励作者适当地增加一个带有TODO或到bug描述当前不接受的类型注释的链接到BUILD文件或者在代码内。

## 3 Python代码风格规范
================================

--------------------
### 3.1 分号
不要在行尾加分号，也不要用分号把两行语句合并到一行。

--------------------
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

--------------------
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

--------------------
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

--------------------
### 3.5 空行
在顶级定义（函数或类）之间要间隔两行。在方法定义之间以及`class`所在行与第一个方法之间要空一行，`def`行后无空行，在函数或方法内你认为合适地方可以使用单空行。

--------------------
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

--------------------
### 3.7 Shebang
大部分`.py`文件不必以`#!`作为文件的开始。根据[PEP-394](https://www.google.com/url?sa=D&q=http://www.python.org/dev/peps/pep-0394/)，程序的main文件应该以`#!/usr/bin/python2`或`#!/usr/bin/python3`起始。

（译者注：在计算机科学中，[Shebang](https://en.wikipedia.org/wiki/Shebang_(Unix))（也称为`Hashbang`）是一个由井号和叹号构成的字符串行（#!），其出现在文本文件的第一行的前两个字符。在文件中存在Shebang的情况下，类Unix操作系统的程序载入器会分析Shebang后的内容，将这些内容作为解释器指令，并调用该指令，并将载有Shebang的文件路径作为该解释器的参数。例如，以指令`#!/bin/sh`开头的文件在执行时会实际调用`/bin/sh`程序。）

`#!/usr/bin/python3`类似的行参数用于帮助内核找到Python解释器，但是在导入模块时，将会被忽略。因此只有被直接执行的文件中才有必要加入`#!`。

--------------------
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

--------------------
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

--------------------
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

--------------------
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

--------------------
### 3.12  TODO注释
对于下述情况使用`TODO`注释：临时的，短期的解决方案或者足够好但是不完美的解决方案。

`TODO`注释以全部大写的字符串`TODO`开头，并带有写入括号内的姓名、e-mail地址或其他可以标识负责人或者包含关于问题最佳描述的issue。随后是这里未来应该做什么的说明。

有统一风格的`TODO`的目的是为了方便搜索并了解如何获取更多相关细节。写了`TODO`注释并不保证写的人会亲自解决问题。当你写了一个`TODO`，请注上你的名字。

```Python
# TODO(kl@gmail.com): Use a "*" here for string repetition.
# TODO(Zeke) Change this to use relations.
```

如果`TODO`注释形式为"未来某个时间点会做什么事"的格式，确保要么给出一个非常具体的时间点（例如"将于2009年11月前修复"）或者给出一个非常具体的事件（例如"当所有客户端都能够处理XML响应时就移除此代码"）。

--------------------
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

--------------------
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

--------------------
### 3.15 访问控制
在Python中，对于琐碎又不太重要的访问函数，你应该直接使用公有变量来取代它们，这样可以避免额外的函数调用开销。当添加更多功能时，你可以用`属性（property）`来保持语法的一致性. 

（译者注：重视封装的面向对象程序员看到这个可能会很反感，因为他们一直被教育：所有成员变量都必须是私有的！其实，那真的是有点麻烦啊。试着去接受Pythonic哲学吧！）

另一方面，如果访问更复杂，对于变量的访问开销显著，你应该使用像`get_foo()`和`set_foo()`这样的函数调用（参考[命名](https://google.github.io/styleguide/pyguide.html#s3.16-naming)指南）。如果过去的访问方式是通过属性（property），那么新访问函数不要绑定到property上。这样，任何试图通过老方法访问变量的代码就没法运行，使用者也就会意识到复杂性发生了变化。

--------------------
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
* internal表示仅模块内可用、或者类内保护的或者私有的。
* 单下划线（`_`）开头表示该模块变量与方法是被保护的（linters会标记“被保护的成员变量”）（译者注：`from module import *`不会import）。双下划线（`__`也就是"dunder"）开头的实例变量或者方法表示类内私有（使用命名修饰）。我们不鼓励使用，因为这会对可读性和可测试性有影响，并且不会使得变量`真正`的私有。
* 将相关的类和顶级函数放在同一个模块里。不像Java，没必要限制一个类一个模块。
* 对类名使用大写字母开头的单词（如CapWords, 即Pascal风格），但是模块名应该用小写加下划线的方式（如lower_with_under.py）。尽管已经有很多现存的模块使用类似于CapWords.py这样的命名，但现在已经不鼓励这样做，因为如果模块名碰巧和类名一致，这会让人困扰（例如：我刚刚写的是`import StringIO`还是`from StringIO import StringIO`？）。
* 在*unittest*方法中可能是`test`开头来分割名字的组成部分，即使这些组成部分是使用大写字母驼峰式的。典型的可能模式像：`test<MethodUnderTest>_<state>`，例如`testPop_EmptyStack`是可以的。对于测试方法的命名没有明确的正确方法。

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

--------------------
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

--------------------
### 3.18 函数长度
优先写小而专一的函数。

长函数有时候是合适的，故而函数长度没有硬性的限制。但是如果一个函数超过40行的时候，就要考虑是否要在不影响程序结构的前提下分解函数。保持函数的简短与简洁，这样有利于其他人读懂和修改代码。

在处理一些代码时，可能会发现有些函数很长而且复杂。不要畏惧调整现有代码，如果调整这样的函数非常困难，如难以对报错debug或者希望在几个不同的上下文中使用它的部分代码，那么请考虑将函数拆解成若干个更小更可控的片段。

--------------------
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

如果函数名、末位形参以及返回的类型说明组合太长，那么分行并缩进4个空格。
```Python
def my_method(
    self, first_var: int) -> Tuple[MyLongType1, MyLongType1]:
  ...
```

若是末位形参和返回值类型注释不适合在同一行上，可以换行，缩进为4空格，并保持闭合的括号 ``)`` 和 ``def`` 对齐。
```Python
def my_method(
    self, other_arg: Optional[MyLongType]
) -> Dict[OtherLongType, MyLongType]:
  ...
```

`pylint`允许将右括号移动到新行并与左括号对其，但是这样做可读性会下降。

**No:**
```
def my_method(self,
              other_arg: Optional[MyLongType]
             ) -> Dict[OtherLongType, MyLongType]:
  ...
```

就像上面的例子一样，尽量不要在一个类型注释中进行换行。不过有时类型注释太长无法放入一行，请尽量保持子类型中不被换行。
```Python
def my_method(
    self,
    first_var: Tuple[List[MyLongType1],
                     List[MyLongType2]],
    second_var: List[Dict[
        MyLongType3, MyLongType4]]) -> None:
  ...
```

如果某个命名和类型太长了，考虑使用[别名](https://google.github.io/styleguide/pyguide.html#typing-aliases)。如果没有其他解决方案，在冒号后分行缩进4个空格。

**Yes:**
```Python
def my_function(
    long_variable_name:
        long_module_name.LongTypeName,
) -> None:
  ...
```

**No:**
```Python
def my_function(
    long_variable_name: long_module_name.
        LongTypeName,
) -> None:
  ...
```

#### 3.19.3 前置声明
若需要使用一个当前模块尚未定义的类名，例如需要类声明内部的类，或者你需要使用后续定义的类，请使用类名的字符串。
```Python
class MyClass:

  def __init__(self,
               stack: List["MyClass"]) -> None:
```

#### 3.19.4 默认值
根据[PEP-008](https://www.python.org/dev/peps/pep-0008/#other-recommendations)，只有在同时需要类型注释和默认值的时候在`=`前后都加空格。

**Yes:**
```Python
def func(a: int = 0) -> int:
  ...
```

**No:**
```Python
def func(a:int=0) -> int:
  ...
```

#### 3.19.5 NoneType
在Python的类型系统中，`NoneType`是"一等对象"，为了输入方便，`None`是`NoneType`的别名。一个变量若是`None`，则该变量必须被声明。我们可以使用`Union`，但若类型仅仅只是对应另一个其他类型，建议使用`Optional`。

尽量显式而非隐式的使用`Optional`。在PEP-484的早期版本中允许使用`a: Text = None`来替代`a: Optional[Text] = None`，当然现在不推荐这么做了。

**Yes:**
```Python
def func(a: Optional[Text], b: Optional[Text] = None) -> Text:
  ...
def multiple_nullable_union(a: Union[None, Text, int]) -> Text
  ...
```

**No:**
```Python
def nullable_union(a: Union[None, Text]) -> Text:
  ...
def implicit_optional(a: Text = None) -> Text:
  ...
```

#### 3.19.6 类型别名
可以对复杂类型声明别名，别名的命名应为CapWorded（即驼峰命名并且首字符大写）。如果只用于当前模块，应加下划线`_`私有化。

例如，如果模块名和类型名连一起过长:
```Python
_ShortName = module_with_long_name.TypeWithLongName
ComplexMap = Mapping[Text, List[Tuple[int, int]]]
```
其他示例是复杂的嵌套类型和一个函数的多个返回变量（作为元组）。

#### 3.19.7 忽略类型检查
可以通过增加特殊行注释`# type: ignore`来禁止类型检查。

`pytype`对于明确的报错有关闭选项（类似于lint）：
```Python
# pytype: disable=attribute-error
```

#### 3.19.8 对变量注释类型
当一个内部变量具有某种难以推断甚至不可能推断的类型时，可以使用下述方式明确其类型：

[*类型注释*](https://google.github.io/styleguide/pyguide.html#type-comments)：

在行尾增加以`# type`开头的注释：
```Python
a = SomeUndecoratedFunction()  # type: Foo
```

[*注释绑定*](https://google.github.io/styleguide/pyguide.html#annotated-assignments)：

在变量名和赋值之间用冒号和类型注明，和函数参数一致。

```Python
a: Foo = SomeUndecoratedFunction()
```

#### 3.19.9 元组 vs 列表
类型化的Lists只能包含单一类型的元素。但类型化的Tuples可以包含单一类型的元素或者若干个不同类型的元素。因此后者通常被用来注解返回值的类型。
（译者注：注意这里是指的类型注解中的写法。实际Python中，list和tuple都是可以在一个序列中包含不同类型元素的，当然，本质其实list和tuple中放的是元素的引用）

```Python
a = [1, 2, 3]  # type: List[int]
b = (1, 2, 3)  # type: Tuple[int, ...]
c = (1, "2", 3.5)  # type: Tuple[int, Text, float]
```

#### 3.19.10 TypeVars
Python是有[泛型](https://www.python.org/dev/peps/pep-0484/#generics)的，工厂函数`TypeVar`是通用的使用方式。

例如:
```Python
from typing import List, TypeVar
T = TypeVar("T")
...
def next(l: List[T]) -> T:
  return l.pop()
```

TypeVar可以约束类型：
```Python
AddableType = TypeVar("AddableType", int, float, Text)
def add(a: AddableType, b: AddableType) -> AddableType:
    return a + b
```
在`typing`模块预定义好的类型变量是`AnyStr`。它可以用于注解类似`bytes`，`unicode`以及一些相似类型。
```Python
from typing import AnyStr
def check_length(x: AnyStr) -> AnyStr:
  if len(x) <= 42:
    return x
  raise ValueError()
```

#### 3.19.11 字符串类型
如何正确的注释字符串的相关类型取决于要使用的Python版本。

对于只有Python3的代码，更倾向于使用`str`。`Text`也可以用，但是两个不要混用，保持风格一致。

对于Python2兼容的代码，应使用`Text`。在一些很罕见的情况下，`str`可能更合理。一般来说，当在不同Python版本之间返回值类型不同的时候通常是为了照顾兼容性。避免使用`unicode`，因为它在Python3中不存在。

造成这种差异的原因是因为，在不同的python版本中，`str`意义不同。

**No:**
```Python
def py2_code(x: str) -> unicode:
  ...
```

对于处理二进制数据的代码，请使用`bytes`。

**Yes:**
```Python
def deals_with_binary_data(x: bytes) -> bytes:
  ...
```

对于处理文本数据的针对Python2兼容的代码（Python2中的`str`或者`unicode`类型，Python3中的`str`类型），应使用`Text`。对于只有Python3的处理文本数据的代码，优先使用`str`。
```Python
from typing import Text
...
def py2_compatible(x: Text) -> Text:
  ...
def py3_only(x: str) -> str:
  ...
```

如果既可以是二进制也可以是文本，那么使用`Union`和合适的文本类型，并按照之前规则使用合适的文本类型注释。
```Python
from typing import Text, Union
...
def py2_compatible(x: Union[bytes, Text]) -> Union[bytes, Text]:
  ...
def py3_only(x: Union[bytes, str]) -> Union[bytes, str]:
  ...
```

如果一个函数中所有的字符串类型始终一致，例如前文的例子中返回值类型和参数类型是一致的，那么使用[`AnyStr`](https://google.github.io/styleguide/pyguide.html#typing-type-var)。

像这样写能够简化代码向Python3的迁移过程。

#### 3.19.12 类型的导入
对于`typing`模块的类的导入，请直接导入类本身。你可以显示的在一行中从从`typing`模块导入多个特定的类，如：
```Python
from typing import Any, Dict, Optional
```

以此方式从`typing`模块导入的类将被加入到本地的命名空间，因此所有`typing`模块中的类都应被视为关键字，不要在代码中定义并覆盖它们。若这些类和现行代码中的变量或者方法发生命名冲突，可以考虑使用`import x as y`的导入形式：
```Python
from typing import Any as AnyType
```

#### 3.19.13 条件导入
在一些特殊情况下，比如当在运行时需要避免类型检查所需的一些导入时，可能会用到条件导入。但这类方法并不推荐，首选方法应是重构代码使类型检查所需的模块可以在顶层导入。

仅用于类型注解的导入可以放在`if TYPE_CHECKING:`语句块内：
* 通过条件导入引入的类的注解须是字符串string，这样才能和python3.6之前的代码兼容。因为python3.6之前，类型注解是会进行求值的.。
* 条件导入引入的包应仅仅用于类型注解，别名也是如此。否则，将引起运行错误，条件导入的包在运行时是不会被实际导入的。
* 条件导入的语句块应放在所有常规导入的语句块之后。
* 在条件导入的语句块的导入语句之间不应有空行。
* 和常规导入一样，请对该导入语句进行排序。

```Python
import typing
if typing.TYPE_CHECKING:
    import sketch
def f(x: "sketch.Sketch"): ...
```

#### 3.19.14 循环依赖
由类型注释引起的循环依赖可能会导致([代码异味（code smells）](https://zh.wikipedia.org/zh-hans/%E4%BB%A3%E7%A0%81%E5%BC%82%E5%91%B3))，这样的代码应当被重构。尽管技术上是可以保留循环引用的，[构建系统（build system）](https://google.github.io/styleguide/pyguide.html#typing-build-deps)不允许这样做因为每个模块都要依赖于其他模块，

将造成循环依赖的模块替换为`Any`导入，并赋予一个有意义的[别名](https://google.github.io/styleguide/pyguide.html#typing-aliases)，并使用从这个模块导入的真实类名（因为任何`Any`的属性都是`Any`）。别名的定义应该和最后的导入语句之间空一行。
```Python
from typing import Any

some_mod = Any  # some_mod.py imports this module.
...

def my_method(self, var: some_mod.SomeType) -> None:
  ...
```

#### 3.19.15  泛型
当注释的时候，尽量将泛型类型注释为类型参数。否则[泛型的参数会被认为是`Any`](https://www.python.org/dev/peps/pep-0484/#the-any-type).
```Python
def get_names(employee_ids: List[int]) -> Dict[int, Any]:
  ...
```
```Python
# These are both interpreted as get_names(employee_ids: List[Any]) -> Dict[Any, Any]
def get_names(employee_ids: list) -> Dict:
  ...

def get_names(employee_ids: List) -> Dict:
  ...
```
若实在要用`Any`作为泛型类型，请显式的使用它。但在多数情况下，[`TypeVar`](https://google.github.io/styleguide/pyguide.html#typing-type-var)通常可能是更好的选择：

```Python
def get_names(employee_ids: List[Any]) -> Dict[Any, Text]:
"""Returns a mapping from employee ID to employee name for given IDs."""
```

```Python
T = TypeVar('T')
def get_names(employee_ids: List[T]) -> Dict[T, Text]:
"""Returns a mapping from employee ID to employee name for given IDs."""
```

## 4 最后的话
================================
***请务必保持代码的一致性（BE CONSISTENT）***

如果你正在编辑代码，花几分钟看一下周边代码，然后决定风格。如果它们在所有的算术操作符两边都使用空格，那么你也应该这样做。如果它们的注释都用标记包围起来，那么你的注释也要这样。

制定风格指南的目的在于让代码有规可循，这样人们就可以专注于“你在说什么”，而不是“你在怎么说”。我们在这里给出的是全局的规范，但是本地的规范同样重要。如果你加到一个文件里的代码和原有代码大相径庭，它会让读者不知所措。请避免这种情况。