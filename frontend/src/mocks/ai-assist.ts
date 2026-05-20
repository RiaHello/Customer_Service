import type { ApiResponse } from '../types/auth'
import type { AIAssistInfo, SuggestReply } from '../types/ai-assist'

// Mock AI 辅助信息数据（按工单 ID 索引）
export const mockAIAssistData: Record<number, AIAssistInfo> = {
  1000: {
    ticket_id: 1000,
    intent: {
      level1: 'IT问题',
      level2: '账户设置',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 1,
      query_domains: {
        'IT问题': 2,
        '账户问题': 1
      },
      last_updated: '2026-05-20 10:45:00'
    },
    suggested_keywords: ['个人资料', '账户设置', '修改信息']
  },
  1001: {
    ticket_id: 1001,
    intent: {
      level1: 'IT问题',
      level2: '系统故障',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 1,
      query_domains: {
        'IT问题': 3,
        '系统问题': 2
      },
      last_updated: '2026-05-20 10:30:00'
    },
    suggested_keywords: ['订单列表', '页面空白', '系统故障']
  },
  1002: {
    ticket_id: 1002,
    intent: {
      level1: '财务问题',
      level2: '退款咨询',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 1,
      query_domains: {
        '财务问题': 1,
        'IT问题': 2
      },
      last_updated: '2026-05-20 10:15:00'
    },
    suggested_keywords: ['退款', '到账时间', '支付方式']
  },
  1003: {
    ticket_id: 1003,
    intent: {
      level1: 'IT问题',
      level2: '账户安全',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 1,
      query_domains: {
        'IT问题': 4,
        '账户问题': 2
      },
      last_updated: '2026-05-20 09:45:00'
    },
    suggested_keywords: ['账户锁定', '密码错误', '安全验证']
  },
  2001: {
    ticket_id: 2001,
    intent: {
      level1: 'IT问题',
      level2: '硬件故障',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 5,
      query_domains: {
        'IT问题': 5,
        '硬件问题': 3
      },
      last_updated: '2026-05-20 11:00:00'
    },
    suggested_keywords: ['电脑开机', '电源故障', '硬件检测']
  },
  2002: {
    ticket_id: 2002,
    intent: {
      level1: 'IT问题',
      level2: '邮件系统',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 6,
      query_domains: {
        'IT问题': 3,
        '邮件问题': 2
      },
      last_updated: '2026-05-20 10:58:00'
    },
    suggested_keywords: ['Outlook', '邮件接收', '网络配置']
  },
  2003: {
    ticket_id: 2003,
    intent: {
      level1: 'IT问题',
      level2: '打印机故障',
      is_ambiguous: false
    },
    user_profile: {
      user_id: 7,
      query_domains: {
        'IT问题': 4,
        '打印问题': 2
      },
      last_updated: '2026-05-20 10:50:00'
    },
    suggested_keywords: ['打印机', '网络连接', '离线状态']
  }
}

// Mock API: 获取 AI 辅助信息
export function mockGetAIAssist(ticketId: number): ApiResponse<AIAssistInfo> {
  const assistInfo = mockAIAssistData[ticketId]

  if (!assistInfo) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  return {
    code: 200,
    message: 'success',
    data: assistInfo
  }
}

// Mock API: 生成建议回复
export function mockSuggestReply(ticketId: number): ApiResponse<SuggestReply> {
  // 根据工单 ID 生成不同的建议回复
  const suggestedReplies: Record<number, string> = {
    1000: '您好！修改个人资料很简单，您可以按照以下步骤操作：1. 登录您的账户；2. 进入"个人中心"页面；3. 点击"编辑资料"按钮；4. 修改您需要更新的信息后点击保存即可。如果您在操作过程中遇到任何问题，请随时告诉我。',
    1001: '您好！根据您的描述，订单列表页面显示空白可能是由于浏览器缓存或系统临时故障导致的。建议您先尝试清除浏览器缓存并刷新页面，或者使用隐私模式打开网站重试。如果问题仍未解决，请提供您的账号信息，我会进一步协助您排查。',
    1002: '您好！关于退款到账时间，如果您使用的是支付宝支付，通常退款会在审核通过后的1-3个工作日内到账。您可以在"我的订单"中查看退款进度。如果超过预计时间仍未到账，请您提供订单号，我会帮您进一步查询。',
    1003: '您好！我看到您的账户因多次密码错误已被锁定。为了保护您的账户安全，我已经帮您解锁账户。建议您使用手机验证码登录后，立即修改密码。同时，为了提高账户安全性，建议您开启双因素认证功能。',
    2001: '您好！电脑无法开机的问题通常有以下几种可能原因：1. 电源线松动或电源适配器故障；2. 主板或内存硬件故障；3. BIOS 设置异常。建议您先检查：电源指示灯是否亮起？按电源键是否有任何声音或风扇转动？请告诉我这些信息，我会进一步协助您排查。如果需要现场支持，我可以为您安排 IT 技术人员上门检修。',
    2002: '您好！Outlook 收不到邮件的问题通常与以下原因有关：1. 网络连接问题（请检查网络是否正常）；2. 邮箱服务器设置不正确（请确认 POP/IMAP/SMTP 配置）；3. 防火墙或杀毒软件拦截。建议您先尝试：打开 Outlook → 文件 → 账户设置 → 测试账户设置。如果测试失败，请告诉我具体的错误信息，我会进一步协助您。',
    2003: '您好！打印机显示离线状态通常是网络连接问题。建议您按以下步骤排查：1. 检查打印机是否开机，指示灯状态；2. 检查网络线是否插紧，或 Wi-Fi 连接是否正常；3. 在电脑上打开"设备和打印机"，右键点击打印机选择"查看正在打印什么"，取消所有打印任务后重启打印机。如果问题仍未解决，请告诉我打印机型号，我会提供更详细的排查步骤。'
  }

  const reply =
    suggestedReplies[ticketId] ||
    '您好！感谢您的耐心等待。我正在为您查询相关信息，请稍候片刻，我会尽快为您提供详细的解决方案。'

  return {
    code: 200,
    message: 'success',
    data: {
      suggested_reply: reply
    }
  }
}
