# automation_operation
### 0.项目简介
数据产品已经搭建起来，数据审核和处理方式为完全手动，处理效率较低达不到预期要求，于是需要对整个产品数据处理流程进行升级迭代。
整个流程包括：数据计算规则更新、数据异常指标选择、异常数据处理、数据上线

**0.1项目内容：**
优化了异常筛查指标：提高异常筛查效果提升100%以上，并大幅降低识别错误率
提出新的运营技巧：将绝大多数的异常数据规则更新时间缩短90%（从几天到几分钟）
搭建自动化运营框架：大幅度提升运营效率（从纯手动处理到80%以上步骤自动运行）
成果：优化异常筛查指标、大幅提高运营效率，并提高了数据更新的及时性。从原本的需要3天到优化后的1天就能完成从规则更新到数据重算的过程。


**0.2产出：** 
多个 自动化处理Python脚本+可视化审核可视化页面（html）+异常筛查结果输出（excel文件）

**0.3工具栈：** pandas(python) + 存储过程 + bokeh (python)

**0.4 图片目录**
1. 数据审核自动化
2. 新规则处理流程图
3. 数据审核可视化页面
4. 数据审核日志

### 1.数据审核
1.1 审核流程图：

<img src="https://github.com/VeeDou/automation_operation-/blob/master/%E8%87%AA%E5%8A%A8%E5%8C%96%E8%BF%90%E8%90%A5/%E6%95%B0%E6%8D%AE%E5%AE%A1%E6%A0%B8%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96/%E6%95%B0%E6%8D%AE%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96%E5%AE%A1%E6%A0%B8_%E6%B5%81%E7%A8%8B%E5%9B%BE.png" width = "400" height = "450" alt="数据审核" 
align=center>

1.2 审核代码主函数：
<img src="https://github.com/VeeDou/automation_operation-/blob/master/%E8%87%AA%E5%8A%A8%E5%8C%96%E8%BF%90%E8%90%A5/%E6%95%B0%E6%8D%AE%E5%AE%A1%E6%A0%B8%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96/%E4%B8%BB%E8%A6%81%E6%B5%81%E7%A8%8B%E7%9A%84%E4%BB%A3%E7%A0%81.png" width = "800" height = "400" alt="数据审核" 
align=center>


### 2.新规则处理流程图
这是规则更新的流程，需要将新规则放入txt文件，然后运行脚本读取文件，自动生产数据入库sql，人工检查无误后，执行sql语句更新规则。
<img 
src="https://github.com/VeeDou/automation_operation-/blob/master/%E8%87%AA%E5%8A%A8%E5%8C%96%E8%BF%90%E8%90%A5/%E8%A7%84%E5%88%99%E6%9B%B4%E6%96%B0%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96/C9918B50-3D4B-4600-8D0E-578A37AE70EC.png" width = "500" height = "300" alt="新规则处理" 
align=center>

### 3.数据审核可视化页面
该文件为python脚本运行中自动输出，可辅助进行快速数据审核（文件为htmL,一个文件500个小程序）
<img 
src="https://github.com/VeeDou/automation_operation-/blob/master/%E8%87%AA%E5%8A%A8%E5%8C%96%E8%BF%90%E8%90%A5/%E6%95%B0%E6%8D%AE%E5%AE%A1%E6%A0%B8%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96/%E6%95%B0%E6%8D%AE%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96%E5%AE%A1%E6%A0%B8_%E5%8F%AF%E4%BA%A4%E4%BA%92%E5%9B%BE%E8%A1%A8.png" width = "800" height = "600" alt="可视化审核" 
align=center>


### 4.数据审核日志
该文件为python脚本运行中自动输出，可辅助记录异常数据
<img 
src="https://github.com/VeeDou/automation_operation-/blob/master/%E8%87%AA%E5%8A%A8%E5%8C%96%E8%BF%90%E8%90%A5/%E6%95%B0%E6%8D%AE%E5%AE%A1%E6%A0%B8%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%8C%96/%E5%8D%8A%E8%87%AA%E5%8A%A8%E5%BC%82%E5%B8%B8%E5%AE%A1%E6%A0%B8%E6%97%A5%E5%BF%97.png" width = "800" height = "600" alt="可视化审核" 
align=center>
