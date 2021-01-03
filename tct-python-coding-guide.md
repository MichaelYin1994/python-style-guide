## 0 背景
================================

@作者：[鱼丸粗面](https://github.com/MichaelYin1994)（zhuoyin94@163.com）

@致谢：
- [谷歌Python代码风格指南-中文翻译](https://github.com/shendeguize/GooglePythonStyleGuideCN)
- [Google 开源项目风格指南 (中文版)](https://github.com/zh-google-styleguide/zh-google-styleguide)

@参考文献：
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [编写可读代码的艺术](https://book.douban.com/subject/10797189/)：Duncan S P. The Art of Readable Code[J]. Software Quality Professional, 2012, 14(2): 47.
- [代码整洁之道](https://book.douban.com/subject/4199741/)：Martin R C. Clean code: a handbook of agile software craftsmanship[M]. Pearson Education, 2009.

Python是目前主流的脚本语言，被用于Web开发、网络爬虫、数据分析等方方面面。这本指南主要包含的是针对Python的编程准则，用于规范团队的风格，便于新的程序员快速融入团队，也为Python的代码审查提供一个基础的标准。

本指南总共包含4个章节：
- **代码检视工具**：阐明了如何利用常见的IDE（例如Visual Studio Code，或者Pycharm）对代码进行检查。
- **基本命名规则**：规定了针对Python编码过程中，包（Packages）、模块（Modules）、类（class）等的命名规范与风格，并包含了一系列的具体建议。
- **Python编码风格与规范**：规定了Python编码过程中的风格与规范。
- **单元测试**：规定了针对各个级别的单元测试文件的撰写。

本指南的撰写，主要参考了上述的参考文献。**针对本指南的运行、复制、分发、学习、修改并改进请注明出处**。基于本指南，我们开源了一个自然语言处理的[小型项目](https://github.com/MichaelYin1994/textrank)作为该指南的模板项目，基于本指南的一切命名、注释、单元测试等规范可参考该项目的编码实现。

---

## 1 代码检视工具
================================

### 1.1 Lint
请使用该[pylintrc](https://github.com/MichaelYin1994/textrank/blob/master/pylintrc)对你的代码运行`pylint`。

`pylint`是一个在Python源代码中查找bug的工具。对于C和C++这样的不那么动态的（强制类型）语言，这些bug通常由编译器来捕获。由于Python的动态特性，`pylint`生成的有些警告可能不对，不过伪告警应该相对较少。

但是需要注意的是，我们不应完全遵照`pylint`的评审结果进行编码，更应该利用其优势，在某些场景下可以抑制警告，或者忽略警告。抑制不准确的警告，以便能够将其他警告暴露出来。你可以通过设置一个行级别的注释来抑制警告。例如:
```Python
dict = 'something awful'  # Bad Idea... pylint: disable=redefined-builtin
```
`pylint`警告是以符号名(如`empty-docstring`)来标识的。如果警告的符号名不够见名知意，那么请对其增加一个详细解释。采用这种抑制方式的好处是我们可以轻松查找抑制并回顾它们。

你可以使用命令`pylint --list-msgs`来获取pylint告警列表。你可以使用命令 `pylint --help-msg=C6409`，以获取关于特定消息的更多信息。

在函数体中`del`未使用的变量可以消除参数未使用告警。但是总要记得要加一条注释说明你为何`del`它们，注释使用"Unused"就可以，例如：
```Python
def viking_cafe_order(spam, beans, eggs=None):
    del beans, eggs  # Unused by vikings.
    return spam + spam + spa
```
其他消除这个告警的方法还有使用`_`标识未使用参数，或者给这些参数名加上前缀 `unused_`，或者直接把它们赋值给`_`。这些方法都是允许的，但是已经不再被鼓励使用。前两种方式会影响到通过参数名传参的调用方式，而最后一种并不能保证参数确实未被使用。

### 1.2 pylint在Visual Studio Code中的配置
pylint在Visual Studio Code中的配置

### 1.3 pylint在Pycharm中的配置
pylint在Pycharm中的配置

---

## 2 基本命名规则
================================

### 2.1 基本命名约定（强制）
模块名命名范式：`module_name`，包名命名范式：`package_name`，类名命名范式：`ClassName`，方法名命名范式：`method_name`，异常名命名范式：`ExceptionName`，函数名命名范式：`function_name`，全局常量命名范式：`GLOBAL_CONSTANT_NAME`，全局变量命名范式：`global_var_name`，实例命名范式：`instance_var_name`，函数命名范式：`function_parameter_name`，局部变量命名范式`local_var_name`。

Python之父Guido的命名指导建议：
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

命名过程中，应当注意：
* internal表示仅模块内可用、或者类内保护的或者私有的。
* 单下划线（`_`）开头表示该模块变量与方法是被保护的。双下划线（`__`也就是"dunder"）开头的实例变量或者方法表示类内私有（使用命名修饰），我们不鼓励使用，因为这会对可读性和可测试性有影响，并且不会使得变量`真正`的私有。
* 将相关的类和顶级函数放在同一个模块里。不像Java，没必要限制一个类一个模块。
* 对类名使用大写字母开头的单词（如CapWords），但是模块名应该用小写加下划线的方式（如lower_with_under.py）。尽管已经有很多现存的模块使用类似于CapWords.py这样的命名，但现在已经不鼓励这样做，因为如果模块名碰巧和类名一致，这会让人困扰（例如：是`import StringIO`还是`from StringIO import StringIO`？二者会让人产生困扰）。
* 在*unittest*方法中可能是`test`开头来分割名字的组成部分，即使这些组成部分是使用大写字母驼峰式的。典型的可能模式像：`test<MethodUnderTest>_<state>`，例如`testPop_EmptyStack`是可以的。对于测试方法的命名没有明确的正确方法。
* Python文件拓展名必须为`.py`，不可以包含`-`（中划线），这保证了能够被正常import和单元测试。

### 2.2 命名过程中应当避免的情况（强制）
命名过程中应当避免以下的一系列情况：
* 单字符名字，除非是以下特殊案例：
  * 计数器或者迭代器（例如`i, j, k, v`等等）。
  * 作为`try/except`中异常声明的`e`。
  * 作为`with`语句中文件对象的`f`。

    请注意不要滥用单字符命名。一般来说，变量名的描述程度应当与命名空间的范围成比例。例如对于变量`i`应该在5行代码块以内有效，如果对于多段嵌套代码含义则显得过于模糊。
* `-`横线，不应出现在任何包名或模块名内。
* `__double_leading_and_trailing_underscore__` 首尾都双下划线的名字，这种名字是Python的内置保留名字。
* 有冒犯性质的名字，例如不文明词汇，侮辱性词汇。
* 空泛的名字。好的名字应当描述变量的目的或者它承载的值。例如某个函数的返回值为输入数组`x`的算平方和，那么`sum_squares`比`retval`这样的名字要好。因此需要尽量避免使用`tmp`、`retval`、`foo`这样的词。

### 2.3 命名过程中的应当尽量遵守的准则
在命名过程中，应当尽量遵守以下的一系列准则：
* 名字不让人产生误解。阅读你代码的人应该理解你的本意，并且不会产生歧义。使用某一个名字之前，要吹毛求疵一点，可以想象一下你的名字会被误解成什么。最好的名字是不会存在误解。例如在写一段数据库操作的代码的时候，采用如下的代码
    ```Python
    results = database.all_objects.filter("year <= 2011")
    ```
    这里的问题是，`filter`是个二义性的单词。我们此处不清楚这个词在这里到底是“挑出”还是“除去”。因此此处最好避免采用`filter`这个词。
* 使用专业的单词。例如不用`get`，而是根据语境使用`fetch`或者`download`可能会更好，再例如`size()`在树中应该用`height()`表示高度，`num_nodes()`表示节点数，用`memory_bytes()`表示内存中所占的空间。但是这由编码的环境所决定，不需要严格遵守。
* 依据使用的语境，使用更有表现力的词汇，例如：

    | 单词   |  更多选择                                     |
    | ----- | ---------------------------------------- |
    | send  | deliver、dispatch、 announce、 distribute、route |
    | find  | search、extract、locate、recover            |
    | start | launch、create、begin、open                 |
    | make  | create、set up、build、generate、compose、add、new |
* 命名过程中，尽量为变量名附加更多的信息。一个变量就像是一个小小的注释，因此如果关于某个变量如果有什么重要信息，那么值得将额外的“词”添加进名字里。例如如果一个`id`字符串是十六进制的，可以命名为`hex_id`。

---

## 3 Python编码注释规范
================================

---

## 3 Python编码风格与规范
================================


---

## 4 单元测试
================================