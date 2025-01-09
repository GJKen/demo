# 先决条件

假设你已经:

- [x] 拥有了一个域名.
- [x] 域名备案已解决.

# Cloudflare 添加域

我们进入 https://dash.cloudflare.com

![](https://github.com/user-attachments/assets/a3b248b9-2390-4b32-a1ff-d653ffd15de9)

输入自己的域名点击继续, 然后选择底部的 Free 计划.

![](https://github.com/user-attachments/assets/33e34c98-27d5-486d-805a-4868af664c04)

复制 dns 名称服务器.

![](https://github.com/user-attachments/assets/d109601c-b13c-4d88-accf-60b4b87503a5)

然后转到你的域名提供服务商, 添加 dns 记录.

![](https://github.com/user-attachments/assets/17bbf19e-0e82-4efb-a5c2-3eee560a47d2)

# 填写 DNS 记录.

回到 Cloudflare 面板, 进入 dns 记录, 按照下图添加 `CNAME` 和 `A` 记录.

![](https://github.com/user-attachments/assets/c061170c-cd32-4097-a184-67b248687457)

```
185.199.108.153

185.199.109.153

185.199.110.153

185.199.111.153
```

# Github Page 设置自定义域名

![](https://github.com/user-attachments/assets/dca11df0-b807-4fb3-adab-7eab63359e85)

填写并点击 Save 之后会提示你等待一会.

![](https://github.com/user-attachments/assets/34e7bc05-f526-41b7-af22-1bb2f2dfd729)

提示`DNS check successful`代表完成, 之后就可以通过www+你的域名进行访问了.

![](https://github.com/user-attachments/assets/ccc047f5-efbe-4132-b9ab-94e91980394a)