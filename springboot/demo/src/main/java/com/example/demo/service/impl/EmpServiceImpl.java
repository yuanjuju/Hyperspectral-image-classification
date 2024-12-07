package com.example.demo.service.impl;
import com.example.demo.mapper.EmpMapper;
import com.example.demo.pojo.Emp;
import com.example.demo.pojo.PageBean;
import com.example.demo.service.EmpService;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class EmpServiceImpl implements EmpService {
    @Autowired private EmpMapper empMapper;
    @Override
   public PageBean page(Integer page, Integer pageSize, String name, Short gender, LocalDateTime begin, LocalDateTime end){
        PageHelper.startPage(page,pageSize);
        List<Emp> emps = empMapper.list(name,gender,begin,end);
        Page<Emp> p = (Page<Emp>) emps;
       PageBean pageBean = new PageBean(p.getTotal(),p.getResult());
       return pageBean;
   }
   @Override
    public  void delete(List<Integer> ids){
        empMapper.delete(ids);
   }
   @Override
   public Emp login(Emp emp){
        return empMapper.getByUsernameAndPassword(emp);
   }
}
