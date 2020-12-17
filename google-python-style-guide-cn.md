背景
================================

Python 是 Google主要的脚本语言。这本风格指南主要包含的是针对python的编程准则。

为帮助读者能够将代码准确格式化，我们提供了针对[Vim的配置文件](https://google.github.io/styleguide/google_python_style.vim)。对于Emacs用户，保持默认设置即可。许多团队使用[yapf](https://github.com/google/yapf/)作为自动格式化工具以避免格式不一致。

Python语言规范
================================

### 2.1 Lint
使用该 [pylintrc](https://google.github.io/styleguide/pylintrc)对你的代码运行`pylint`

#### 2.1.1 定义:
`pylint`是一个在Python源代码中查找bug的工具。对于C和C++这样的不那么动态的(译者注: 原文是less dynamic)语言，这些bug通常由编译器来捕获。由于Python的动态特性，有些警告可能不对。不过伪告警应该相对较少。

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

#### 2.3.3 建议
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

#### 2.5.4 建议
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

#### 2.6.4 建议
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

#### 2.7.4 建议
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
### 2.8 默认迭代器和操作符
如果类型支持，就使用默认迭代器和操作符。比如列表，字典及文件对象等。

### 2.8.1 定义
容器类型，例如字典和列表，定义了默认的迭代器和关系测试操作符（`in`和`not in`）。

### 2.8.2 Pros
默认操作符和迭代器简单且高效。它们直接表达了操作的含义，没有额外的方法调用。使用默认操作符的函数是通用的。它可以用于支持该操作的任何类型。