Page({
  data: {
    messages: [], // 聊天消息列表
    inputValue: "", // 输入框内容
    avatarUrl: undefined, // 用户头像
    floors: [],
    detail: null,
  },

  onLoad() {
    console.log("Index::onReady() is called")
    this.updateFloors();
  },

  updateFloors() {
    const app = getApp();
    const floors = app.globalData.data.floors;
    console.log("Floors: ", floors)
    const n = Object.keys(floors).length;
    let data = [];
    for (let i = 1; i <= n; i++) {
      data.push({
        "id": i,
        ...floors[i]
      });
    }
    console.log("Data: ", floors)
    const detail = this.genShoppingCenterDetail(app.globalData.data);
    console.log("Detail: ", detail)
    this.setData({floors: data, detail: detail});
  },

  genShoppingCenterDetail(data) {
    const app = getApp();
    const parking = app.getParkingLotInfo();
    const n = Object.keys(data.floors).length;
    let prompt = `${data.location}有一家商城，名叫“${data.name}”，共有${n}层楼。\n\n`;
    prompt += `停车场信息：${data.parking}\n`;
    prompt += `当前车位剩余信息：${parking}\n\n`;
    prompt += `各个楼层详细信息如下：\n\n`;
    for (let i = 1; i <= n; i++) {
      const floor = data.floors[i];
      const washroom = floor.washroom ? "有卫生间" : "无卫生间";
      const merchants = floor.merchants.length
      prompt += `### ${i}楼：主要经营${floor.introduction}。这一层${washroom}。这一层共有${merchants}个商家入住，商家列表如下：\n`;
      for (let j = 0; j < merchants; j++) {
        const merchant = floor.merchants[j];
        prompt += `${j+1}、商家：${merchant.name}；主营业务：${merchant.business}；门牌号：${merchant.id}\n`;
      }
      prompt += "\n";
    }
    return prompt;
  },

  navToFloor(e) {
    const floor = e.currentTarget.dataset.floor;
    console.log(`Goto floor ${floor}`)
    wx.navigateTo({
      url: '/pages/floor/index?floor='+floor,
      success: (result) => {},
      fail: (res) => {},
      complete: (res) => {},
    })
  },

  // 输入框内容变化时触发
  onInput(e) {
    this.setData({
      inputValue: e.detail.value,
    });
  },

  // 发送消息
  sendMessage() {
    if (!this.data.avatarUrl) {
      this.getUserProfile(this.sendMessage);
      return;
    }
    const userMessage = this.data.inputValue.trim();
    if (!userMessage) return; // 如果输入为空，则不发送

    // 添加用户消息
    const newMessage = {
      id: Date.now(),
      text: userMessage,
      sender: "user", // 标记为我方消息
    };
    this.setData({
      messages: [...this.data.messages, newMessage],
      inputValue: "", // 清空输入框
    });

    this.getResponse(userMessage, (response) => {
      const botMessage = {
        id: Date.now(),
        text: response,
        sender: "bot", // 标
      };
      this.setData({
        messages: [...this.data.messages, botMessage],
      });
    });

    // 模拟对方回复
    // setTimeout(() => {
    //   const botMessage = {
    //     id: Date.now(),
    //     text: this.getResponse(userMessage),
    //     sender: "bot", // 标记为对方消息
    //   };
    //   this.setData({
    //     messages: [...this.data.messages, botMessage],
    //   });
    // }, 1000); // 延迟1秒回复
  },

  getResponse(userMessage, callback) {
    // return this.getRandomResponse();
    const messages = [
      {
        role: "system",
        content: "你是一个商场客服机器人，你擅长根据客户的问题和兴趣，引导客户到入住商场的相关商家去消费。\n"
                + "你要根据下面提供的商场的具体信息进行回答，超出商场经营范围的内容，请告诉客户我们这里没有这项服务。\n"
                + "以下是商场的具体信息：\n\n"
                + this.data.detail
      },
      {
        role: "user",
        content: userMessage + "\n请根据你们商场信息回答我（引导客户到具体楼层的商家去消费），如果是停车问题，需回答剩余车位数量，请不要超过50个字。"
      }
    ];

    const url = 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions';
    console.log(`Request LLM from ${url}, messages:`, messages)
    wx.request({
      url: url,
      method: 'POST',
      header: {
        "Authorization": "Bearer sk-8eHA12xcZplrkzHirPQoNkYgoS5Mz3gGGjWVyqMMW4g9RgNw",
        "Content-Type": "application/json",
      },
      data: {
        model: "hunyuan-turbo",
        messages: messages,
        stream: false
      },
      success(res) {
        console.log('Response:', res)
        if (res.statusCode === 200) {
          const data = res.data.choices[0].message.content; // 获取响应内容
          callback(data);
        } else {
          wx.showToast({
            title: '请求失败',
            icon: 'none',
          });
          console.error('请求失败:', res);
        }
      },
      fail(err) {
        wx.showToast({
          title: '网络错误',
          icon: 'none',
        });
        console.error('网络错误:', err);
      }
    });
  },

  // 随机回复一句话
  getRandomResponse() {
    const responses = [
      "你好！",
      "今天天气不错！",
      "你在忙什么呢？",
      "哈哈，真有趣！",
      "我明白了。",
      "再聊一会儿吧！",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  },

  getUserProfile(callback) {
    wx.getUserProfile({
      desc: '用于展示用户信息', // 声明用途
      success: (res) => {
        const userInfo = res.userInfo;
        this.setData({
          userInfo: userInfo,
          avatarUrl: userInfo.avatarUrl, // 获取头像 URL
        });
        console.log('用户信息:', userInfo);
        callback();
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err);
      },
    });
  },
});