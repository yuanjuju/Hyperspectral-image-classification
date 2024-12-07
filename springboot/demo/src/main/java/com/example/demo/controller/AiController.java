package com.example.demo.controller;

import com.alibaba.dashscope.aigc.generation.Generation;
import com.alibaba.dashscope.aigc.generation.GenerationParam;
import com.alibaba.dashscope.aigc.generation.GenerationResult;
import com.alibaba.dashscope.common.Message;
import com.alibaba.dashscope.common.Role;
import com.alibaba.dashscope.exception.InputRequiredException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.utils.JsonUtils;
import io.reactivex.Flowable;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.scheduler.Schedulers;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/ai")
@CrossOrigin(origins = "http://localhost:8081") // 跨域配置
public class AiController {

    private final Generation generation;

    @Value("${ai.api.key}")
    private String appKey;

    @Autowired
    public AiController(Generation generation) {
        this.generation = generation;
    }

    /**
     * 用于接收用户的问题并返回完整的回答
     * @param question 用户输入的问题
     * @return AI 完整的回答
     */
    @PostMapping("/send")
    public ResponseEntity<String> aiTalk(@RequestBody String question) {
        System.out.println("接收到问题: " + question);

        // 构建消息体
        Message message = Message.builder().role(Role.USER.getValue()).content(question).build();

        GenerationParam qwenParam = GenerationParam.builder()
                .model(Generation.Models.QWEN_PLUS)
                .messages(Arrays.asList(message))
                .resultFormat(GenerationParam.ResultFormat.MESSAGE)
                .topP(0.8)
                .apiKey(appKey)
                .build();

        // 调用生成方法
        GenerationResult result;
        try {
            result = generation.call(qwenParam);  // 这里是同步调用，等待结果
        } catch (NoApiKeyException e) {
            return ResponseEntity.status(HttpServletResponse.SC_BAD_REQUEST)
                    .body("API 密钥缺失或无效：" + e.getMessage());
        } catch (InputRequiredException e) {
            return ResponseEntity.status(HttpServletResponse.SC_BAD_REQUEST)
                    .body("缺少必需的输入：" + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpServletResponse.SC_INTERNAL_SERVER_ERROR)
                    .body("发生未知错误：" + e.getMessage());
        }

        // 获取完整的回答并返回
        String answer = result.getOutput().getChoices().get(0).getMessage().getContent();
        System.out.println("完整回答: " + answer);

        return ResponseEntity.ok(answer);  // 返回完整的 AI 回答
    }
}


