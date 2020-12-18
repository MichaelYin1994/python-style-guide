背景
================================

Python 是 Google主要的脚本语言。这本风格指南主要包含的是针对python的编程准则。

为帮助读者能够将代码准确格式化，我们提供了针对[Vim的配置文件](https://google.github.io/styleguide/google_python_style.vim)。对于Emacs用户，保持默认设置即可。许多团队使用[yapf](https://github.com/google/yapf/)作为自动格式化工具以避免格式不一致。

Python语言规范
================================

### 2.1 Lint
使用该[pylintrc](https://google.github.io/styleguide/pylintrc)对你的代码运行`pylint`

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

### 2.8.1 定义
容器类型，例如字典和列表，定义了默认的迭代操作符和关系测试操作符（`in`和`not in`）。

### 2.8.2 Pros
默认操作符和迭代器简单且高效。它们直接表达了操作的含义，没有额外的方法调用。使用默认操作符的函数是通用的。它可以用于支持该操作的任何类型。

### 2.8.3 Cons
你没法通过阅读方法名来区分对象的类型（例如，`has_key()`意味着字典）。不过这也是优点。

### 2.8.4 结论
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
如果好处很显然，就明智而谨慎的使用装饰器。装饰器应该遵守和函数一样的导入和命名规则。装饰器的python文档应该清晰的说明该函数是一个装饰器。请为装饰器编写单元测试。 

避免装饰器自身对外界的依赖（即不要依赖于文件，socket，数据库连接等），因为装饰器运行时这些资源可能不可用(由`pydoc`或其它工具导入). 应该保证一个用有效参数调用的装饰器在所有情况下都是成功的.
    
    装饰器是一种特殊形式的"顶级代码". 参考后面关于 :ref:`Main <main>` 的话题. 

    除非是为了将方法和现有的API集成，否则不要使用 ``staticmethod`` .多数情况下，将方法封装成模块级的函数可以达到同样的效果.

    谨慎使用 ``classmethod`` .通常只在定义备选构造函数，或者写用于修改诸如进程级缓存等必要的全局状态的特定类方法才用。

