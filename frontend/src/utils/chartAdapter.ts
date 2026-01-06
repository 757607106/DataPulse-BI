/**
 * 图表数据适配器
 * 将后端返回的 data (rows/columns) 转换为 ECharts 配置
 */
import type { ChatData, ChartType } from '@/types/chat';
import type { EChartsOption } from 'echarts';

/**
 * 将 ChatData 转换为 ECharts Option
 */
export const convertToEChartsOption = (
  data: ChatData,
  chartType: ChartType,
  isDark: boolean = true
): EChartsOption => {
  const { columns, rows } = data;

  if (!rows || rows.length === 0) {
    return getEmptyChartOption(isDark);
  }

  // 主题颜色配置
  const colors = isDark
    ? ['#06B6D4', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#3B82F6']
    : ['#0891B2', '#059669', '#D97706', '#7C3AED', '#DB2777', '#2563EB'];

  switch (chartType) {
    case 'bar':
      return getBarChartOption(columns, rows, colors, isDark);
    case 'line':
      return getLineChartOption(columns, rows, colors, isDark);
    case 'pie':
      return getPieChartOption(columns, rows, colors, isDark);
    case 'scatter':
      return getScatterChartOption(columns, rows, colors, isDark);
    case 'radar':
      return getRadarChartOption(columns, rows, colors, isDark);
    case 'table':
    default:
      // table 类型不返回图表配置，由组件直接渲染表格
      return getEmptyChartOption(isDark);
  }
};

/**
 * 柱状图配置
 */
const getBarChartOption = (
  columns: string[],
  rows: Array<Record<string, any>>,
  colors: string[],
  isDark: boolean
): EChartsOption => {
  // 假设第一列为 X 轴（分类），其余列为数值
  const xAxisData = rows.map(row => row[columns[0]]);
  const series = columns.slice(1).map((col, index) => ({
    name: col,
    type: 'bar' as const,
    data: rows.map(row => row[col]),
    // 渐变色配置 (Teal/Blue 风格)
    itemStyle: {
      color: {
        type: 'linear' as const,
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          {
            offset: 0,
            color: index === 0 ? '#06B6D4' : colors[index % colors.length] // 顶部颜色
          },
          {
            offset: 1,
            color: index === 0 ? '#0891B2' : adjustColorBrightness(colors[index % colors.length], -20) // 底部颜色（加深）
          }
        ]
      },
      borderRadius: [4, 4, 0, 0] // 顶部圆角
    },
    // 鼠标悬停时的高亮效果
    emphasis: {
      itemStyle: {
        color: {
          type: 'linear' as const,
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: adjustColorBrightness(index === 0 ? '#06B6D4' : colors[index % colors.length], 20)
            },
            {
              offset: 1,
              color: index === 0 ? '#06B6D4' : colors[index % colors.length]
            }
          ]
        }
      }
    },
    // 柱子宽度
    barMaxWidth: 40
  }));

  return {
    color: colors,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: isDark ? '#334155' : '#e2e8f0',
      borderWidth: 1,
      textStyle: {
        color: isDark ? '#f1f5f9' : '#0f172a',
        fontSize: 13
      },
      padding: [8, 12],
      // 自定义 tooltip 格式化：将数值格式化为货币格式
      formatter: (params: any) => {
        if (Array.isArray(params)) {
          let result = `<div style="font-weight: 600; margin-bottom: 4px;">${params[0].axisValue}</div>`;
          params.forEach((param: any) => {
            const value = formatCurrency(param.value);
            result += `
              <div style="display: flex; align-items: center; margin-top: 4px;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${param.color}; margin-right: 6px;"></span>
                <span style="flex: 1;">${param.seriesName}:</span>
                <span style="font-weight: 600; margin-left: 12px;">${value}</span>
              </div>
            `;
          });
          return result;
        }
        return `${params.seriesName}: ${formatCurrency(params.value)}`;
      }
    },
    legend: {
      data: columns.slice(1),
      textStyle: {
        color: isDark ? '#cbd5e1' : '#475569',
        fontSize: 12
      },
      itemGap: 16,
      top: 8
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b',
        fontSize: 11,
        // X 轴标签过长时旋转
        rotate: xAxisData.length > 8 ? 30 : 0,
        interval: 0,
        // 截断过长文本
        formatter: (value: string) => {
          if (value.length > 8) {
            return value.substring(0, 7) + '...';
          }
          return value;
        }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b',
        fontSize: 11,
        // Y 轴标签格式化为简写形式 (200k, 1M)
        formatter: (value: number) => {
          return formatNumberShort(value);
        }
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#1e293b' : '#f1f5f9',
          type: 'dashed'
        }
      }
    },
    series
  };
};

/**
 * 调整颜色亮度
 */
const adjustColorBrightness = (color: string, percent: number): string => {
  const num = parseInt(color.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return '#' + (
    0x1000000 +
    (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)
  ).toString(16).slice(1);
};

/**
 * 将数值格式化为货币格式（如 ￥2,642,344）
 */
const formatCurrency = (value: number): string => {
  if (value == null || isNaN(value)) return '-';
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

/**
 * 将数值格式化为简写形式 (200k, 1M, 1B)
 */
const formatNumberShort = (value: number): string => {
  if (value == null || isNaN(value)) return '0';
  
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  
  if (absValue >= 1e9) {
    return sign + (absValue / 1e9).toFixed(1) + 'B';
  } else if (absValue >= 1e6) {
    return sign + (absValue / 1e6).toFixed(1) + 'M';
  } else if (absValue >= 1e3) {
    return sign + (absValue / 1e3).toFixed(1) + 'K';
  }
  return sign + absValue.toFixed(0);
};

/**
 * 折线图配置
 */
const getLineChartOption = (
  columns: string[],
  rows: Array<Record<string, any>>,
  colors: string[],
  isDark: boolean
): EChartsOption => {
  const xAxisData = rows.map(row => row[columns[0]]);
  const series = columns.slice(1).map((col, index) => ({
    name: col,
    type: 'line' as const,
    data: rows.map(row => row[col]),
    smooth: true,
    itemStyle: {
      color: colors[index % colors.length]
    },
    lineStyle: {
      width: 2
    }
  }));

  return {
    color: colors,
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#334155' : '#e2e8f0',
      textStyle: {
        color: isDark ? '#f1f5f9' : '#0f172a'
      }
    },
    legend: {
      data: columns.slice(1),
      textStyle: {
        color: isDark ? '#cbd5e1' : '#475569'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b'
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#1e293b' : '#f1f5f9'
        }
      }
    },
    series
  };
};

/**
 * 饼图配置
 */
const getPieChartOption = (
  columns: string[],
  rows: Array<Record<string, any>>,
  colors: string[],
  isDark: boolean
): EChartsOption => {
  // 假设第一列为名称，第二列为数值
  const data = rows.map(row => ({
    name: row[columns[0]],
    value: row[columns[1]]
  }));

  return {
    color: colors,
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#334155' : '#e2e8f0',
      textStyle: {
        color: isDark ? '#f1f5f9' : '#0f172a'
      }
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        color: isDark ? '#cbd5e1' : '#475569'
      }
    },
    series: [
      {
        name: columns[1] || '数据',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: isDark ? '#0f172a' : '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: isDark ? '#f1f5f9' : '#0f172a'
          }
        },
        labelLine: {
          show: false
        },
        data
      }
    ]
  };
};

/**
 * 散点图配置
 */
const getScatterChartOption = (
  columns: string[],
  rows: Array<Record<string, any>>,
  colors: string[],
  isDark: boolean
): EChartsOption => {
  // 假设前两列为 X、Y 坐标
  const data = rows.map(row => [row[columns[0]], row[columns[1]]]);

  return {
    color: colors,
    tooltip: {
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#334155' : '#e2e8f0',
      textStyle: {
        color: isDark ? '#f1f5f9' : '#0f172a'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b'
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#1e293b' : '#f1f5f9'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      axisLabel: {
        color: isDark ? '#94a3b8' : '#64748b'
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#1e293b' : '#f1f5f9'
        }
      }
    },
    series: [
      {
        type: 'scatter',
        data,
        itemStyle: {
          color: colors[0]
        },
        symbolSize: 10
      }
    ]
  };
};

/**
 * 雷达图配置
 */
const getRadarChartOption = (
  columns: string[],
  rows: Array<Record<string, any>>,
  colors: string[],
  isDark: boolean
): EChartsOption => {
  // 假设第一列为维度名称，其余列为数值
  const indicator = columns.slice(1).map(col => ({ name: col }));
  const data = rows.map(row => ({
    value: columns.slice(1).map(col => row[col]),
    name: row[columns[0]]
  }));

  return {
    color: colors,
    tooltip: {
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDark ? '#334155' : '#e2e8f0',
      textStyle: {
        color: isDark ? '#f1f5f9' : '#0f172a'
      }
    },
    legend: {
      data: rows.map(row => row[columns[0]]),
      textStyle: {
        color: isDark ? '#cbd5e1' : '#475569'
      }
    },
    radar: {
      indicator,
      axisLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#334155' : '#cbd5e1'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: isDark
            ? ['rgba(51, 65, 85, 0.1)', 'rgba(51, 65, 85, 0.2)']
            : ['rgba(241, 245, 249, 0.3)', 'rgba(226, 232, 240, 0.3)']
        }
      }
    },
    series: [
      {
        type: 'radar',
        data
      }
    ]
  };
};

/**
 * 空图表配置（用于无数据或table类型）
 */
const getEmptyChartOption = (isDark: boolean): EChartsOption => {
  return {
    title: {
      text: '暂无数据',
      left: 'center',
      top: 'middle',
      textStyle: {
        color: isDark ? '#64748b' : '#94a3b8',
        fontSize: 16
      }
    }
  };
};
