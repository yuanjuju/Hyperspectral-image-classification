package com.example.demo.controller;
import com.example.demo.pojo.Dept;
import com.example.demo.pojo.Result;
import com.example.demo.service.DeptService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@RestController
public class DeptController {
    @Autowired
    private DeptService deptService;
    @RequestMapping("/Dept")
    public Result list() {
        List<Dept> deptlist=deptService.list();
        return Result.success(deptlist);
    }
    @DeleteMapping("/depts/{id}")
    public Result delete(@PathVariable Integer id){
        deptService.delete(id);
        return Result.success();
    }
    @PostMapping("/depts")
    public Result add(@RequestBody Dept dept){
        deptService.add(dept);
        return Result.success();
    }
}
