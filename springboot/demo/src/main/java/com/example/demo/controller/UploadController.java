package com.example.demo.controller;

import com.example.demo.pojo.Result;
import com.example.demo.utils.AliOSSUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class UploadController {
    @Autowired
    private AliOSSUtils aliOSSUtils;
    @PostMapping("/upload")
    public Result upload(MultipartFile image) throws Exception {
        String url = aliOSSUtils.upload(image);
        return Result.success(url);
    }
}
