# 04. 官方贡献证明 (Contribution Proof) 签名与上链全流程

## 一、什么是 Contribution Proof（贡献证明）？

在大多数区块链与 Web3 项目中，社区成员提交贡献（如文章、视频、开源代码）往往依赖中心化的人工审核或者提交 Google 表单。这种方式极易被抄袭、伪造或者冒名顶替。

**FLOP Labs** 在其协议核心 `technocore_agent.py` 中引入了原生的 **密码学贡献证明（Contribution Proof）** 机制：
> 开发者可以使用自己拥有的 **Technocore DID**，对其发布的开源项目代码仓库（HTTPS URL）和特定的不可篡改版本（Git Commit Hash）进行**链下 Ed25519 签名**。

---

## 二、数据结构标准规范：`technocore-contribution-proof-v1`

一个标准的贡献证明文件是一个结构化的 JSON 文档，规范定义如下：

```json
{
  "schema": "technocore-contribution-proof-v1",
  "did": "did:key:z6MkwBZMeaqfJpg3GPEd4jR719FxNZJmi2YURvxC9bgHozuT",
  "artifact_url": "https://github.com/your-username/FLOP-Technocore-Kit",
  "commit": "4b825dc642cb6eb9a060e54bf8d69288fbee4904",
  "signature": "34k55Fh9QLYIxz876PcmrIuQ_9BW_LTc0lA8TsoohxjdL2yKQD__D7Z6d07FQB2xU8afz8H9GdoodLUe2OUrAQ"
}
```

### 字段说明：
* **`schema`**：固定的标准协议头，当前版本为 `technocore-contribution-proof-v1`；
* **`did`**：贡献者的公钥身份标识；
* **`artifact_url`**：公开可访问的项目绝对 HTTPS 链接（如 GitHub 仓库根目录）；
* **`commit`**：Git 仓库中本次贡献里程碑的完整 40 位十六进制 Commit 哈希；
* **`signature`**：私钥对规范化载荷 `{"artifact_url":..., "commit":..., "schema":"technocore-contribution-v1"}` 生成的 Ed25519 签名。

---

## 三、手把手操作：如何生成属于你的贡献证明

### 步骤 1：完成代码与文档编写并提交至 Git
在本地仓库中提交最新代码：
```bash
git add .
git commit -m "feat: release FLOP Technocore developer kit & documentation"
```

获取最新的 40 位完整 Commit 哈希：
```bash
git rev-parse HEAD
# 例如输出：4b825dc642cb6eb9a060e54bf8d69288fbee4904
```

### 步骤 2：使用官方命令生成数字签名
运行官方内置的 `proof` 指令：
```bash
python technocore_agent.py proof \
  --key /path/to/identity.pem \
  --output proof/contribution-proof.json \
  "https://github.com/your-username/FLOP-Technocore-Kit" \
  "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
```
终端会提示您输入 `identity.pem` 的密码，输入完成后，将自动生成并写入 `proof/contribution-proof.json` 文件！

---

## 四、如何验证贡献证明的真伪？

任何第三方、社区审核者或官方团队，均无需接触您的私钥，即可使用官方命令核验该证明：

```bash
python technocore_agent.py verify-proof proof/contribution-proof.json
```

* **验证成功**：终端无报错退出，密码学数学上 100% 证明：**该 Git 提交是由该 DID 私钥持有者本人亲笔签名发布的，中途绝无任何篡改！**
* **验证失败**：如果有人修改了 Commit 哈希、URL 哪怕一个字符，或者伪造了 DID，程序将直接抛出 `InvalidSignature` 异常！

---

## 五、向官方网络广播与权益锁定

生成 `contribution-proof.json` 后，您拥有了无可争辩的密码学权属：

1. **大厅广播凭证**：
   通过 Agent 向 Technocore 房间广播证明发布通知：
   ```bash
   python technocore_agent.py say lobby "Contribution proof published for FLOP-Technocore-Kit. Verification hash: 4b825dc... Verified by did:key:z6MkwBZM..."
   ```
2. **在官方生态/贡献者申请通道中提交**：
   如官方开放 KOL/贡献者申请通道（或在官方验证者意向表 `flop.finance/apply/validator` 的补充说明栏中），附上您的 GitHub 仓库链接与上述证明签名。这份高标准的密码学实证将使您在成千上万的申请者中脱颖而出，直通核心贡献者权益！
