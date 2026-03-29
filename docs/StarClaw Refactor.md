# StarClaw Refactor

## 增加外部智能体(External)配置功能

在实际使用场景中会存在已经开发的智能体，这里以阿里百炼达模型服务平台（https://bailian.console.aliyun.com/）环境进行举例说明。

### 外部智能体调用样例
这是一个典型的OpenAI接口规范智能体调用样例
```
curl -X POST 'https://dashscope.aliyuncs.com/api/v2/apps/agent/d0a4159be6fa4621a77900cb2a697c67/compatible-mode/v1/responses' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "分析一下招商证券"
        }
      ]
    }
  ],
  "stream": true,
  "background": false
}'
```
- URL 参数: 为智能体调用地址，通常agent id 会包含在这个地址中，如本例中的"d0a4159be6fa4621a77900cb2a697c67"
- 认证参数: "YOUR_API_KEY" 为调用该接口时需要替换的密钥
- 用户消息: input > content > text 为用户输入消息
- 流式输出参数:  stream, 是否使用协议流式输出方式, 默认为true
- 异步执行方式: background, 是否使用异步执行方式, 默认为false 

### 功能要求： 
1，支持外部智能体配置,包括增、删、改、查功能。
2，支持Agent通过接口进行调用

#### 界面要求：
1, 在Console 项目中， 增加External菜单, 位置于左侧菜单Agent 菜单中(MCP菜单下方，Configuration上方)。
2, 界面风格参考Skills模块界面，使用状态最好使用Tools模块界面中的ridio按钮方式。

#### 后端要求:
1, 在目前项目架构下开发，存储配置环境，接口方式与其他模块保持一致。