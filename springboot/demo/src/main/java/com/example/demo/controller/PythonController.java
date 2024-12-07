package com.example.demo.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import com.fasterxml.jackson.databind.JsonNode;

@RestController
@RequestMapping("/api")
public class PythonController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/uploadfile")
    public ResponseEntity<Object> handleFileUpload(@RequestParam("file") MultipartFile file) {
        System.out.println("File received, forwarding to Flask server...");

        // Flask 服务的 URL
        String flaskUrl = "http://localhost:5000/api/upload"; // 替换为实际的 Flask 服务地址

        // 准备转发请求的表单数据
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", file.getResource());

        // 创建请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // 创建HttpEntity
        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            // 转发请求到 Flask 后端
            ResponseEntity<String> response = restTemplate.exchange(flaskUrl, HttpMethod.POST, requestEntity, String.class);

            // 获取 Flask 返回的响应体 (假设它是一个包含 predictions 字段的 JSON)
            String flaskResponse = response.getBody();

            // 使用 Jackson 解析 Flask 返回的 JSON 字符串
            // 如果 Flask 返回的是 JSON 格式的字符串（例如 {"predictions": [1, 2, 3]}）
            JsonNode jsonNode = new ObjectMapper().readTree(flaskResponse);

            // 如果 Flask 返回了 predictions 字段
            if (jsonNode.has("predictions")) {
                return ResponseEntity.ok().body(jsonNode);  // 直接将 Flask 的 JSON 响应返回给前端
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ResponseMessage("No predictions found", ""));
            }

        } catch (HttpClientErrorException e) {
            // 如果请求失败（如4xx、5xx错误），返回具体的错误信息
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ResponseMessage("Error forwarding file", e.getMessage()));
        } catch (RestClientException e) {
            // 其他 RestTemplate 相关的异常（如网络问题）
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ResponseMessage("Error forwarding file", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ResponseMessage("Error processing Flask response", e.getMessage()));
        }
    }

    // 定义一个内部类来封装 JSON 响应
    public static class ResponseMessage {
        private String message;
        private String predictions;

        // 构造函数
        public ResponseMessage(String message, String predictions) {
            this.message = message;
            this.predictions = predictions;
        }

        // Getter 和 Setter 方法
        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public String getPredictions() {
            return predictions;
        }

        public void setPredictions(String predictions) {
            this.predictions = predictions;
        }
    }
}
