> 今日新发现反爬虫规则

- cookie能持续有效，通过cookie来ban
- 无cookie 无法打开商铺详情页面，可能和 x-mss-trace-id 有关
- 这个 x-mss-trace-id 可能和token有关

> 措施

- 但凡cookies失效后，请求列表，更换cookie