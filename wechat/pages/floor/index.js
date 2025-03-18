// pages/floor/index.js
Page({
  data: {
    floor: null
  },
  onLoad(options) {
    console.log("Floor::onLoad()", options)
    const app = getApp()
    const floor = app.globalData.data.floors[options.floor];
    console.log(`Floor ${options.floor}:`, floor)
    wx.setNavigationBarTitle({
      title: options.floor + "楼商家列表",
    });
    this.setData({floor: floor})
  },
})