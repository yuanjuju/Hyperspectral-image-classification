package com.example.demo.utils;

import com.aliyuncs.DefaultAcsClient;
import com.aliyuncs.IAcsClient;
import com.aliyuncs.dysmsapi.model.v20170525.SendSmsRequest;
import com.aliyuncs.dysmsapi.model.v20170525.SendSmsResponse;
import com.aliyuncs.exceptions.ClientException;
import com.aliyuncs.profile.DefaultProfile;

/**
 * 短信发送工具类
 */
public class SMSUtils {

    /**
     * 发送短信
     * @param signName 签名
     * @param templateCode 模板
     * @param phoneNumbers 手机号
     * @param param 参数（验证码等）
     */
    public static void sendMessage(String signName, String templateCode, String phoneNumbers, String param) {
        // 创建阿里云短信服务的客户端配置
        DefaultProfile profile = DefaultProfile.getProfile("cn-hangzhou",
               ,  // 你的AccessKey ID
               ); // 你的AccessKey Secret
        IAcsClient client = new DefaultAcsClient(profile);

        // 创建短信发送请求对象
        SendSmsRequest request = new SendSmsRequest();

        // 设置请求参数
        request.setSysRegionId("cn-hangzhou"); // 设置区域
        request.setPhoneNumbers(phoneNumbers); // 设置目标手机号码
        request.setSignName(signName); // 设置短信签名
        request.setTemplateCode(templateCode); // 设置短信模板代码

        // 设置模板中的参数（验证码等，传入 JSON 格式的字符串）
        // 例如模板中定义了 ${code}，那么 param 就是验证码
        request.setTemplateParam("{\"code\":\"" + param + "\"}");

        try {
            // 发送请求并接收响应
            SendSmsResponse response = client.getAcsResponse(request);

            // 输出发送结果
            if ("OK".equals(response.getCode())) {
                System.out.println("短信发送成功");
            } else {
                System.out.println("短信发送失败，错误码：" + response.getCode() + ", 错误信息：" + response.getMessage());
            }
        } catch (ClientException e) {
            e.printStackTrace();
        }
    }
}
