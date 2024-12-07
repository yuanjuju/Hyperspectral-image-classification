package com.example.demo.controller;

import com.example.demo.pojo.PageBean;
import com.example.demo.pojo.Result;
import com.example.demo.service.EmpService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
public class Empcontroller {
    @Autowired private EmpService empService;

    @GetMapping("/emps")
    public Result page(@RequestParam(defaultValue = "1") Integer page, @RequestParam(defaultValue = "10") Integer pageSize, String name,
                       Short gender, LocalDateTime begin, LocalDateTime end)
    {

        PageBean pageBean= empService.page(page,pageSize,name,gender,begin,end);
        return Result.success(pageBean);

    }

    @DeleteMapping("/emps/{ids}")
    public Result delete(@PathVariable("ids") List<Integer> ids)
    {
        empService.delete(ids);
        return Result.success();
    }
}
