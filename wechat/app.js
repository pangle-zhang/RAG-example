const localData = require('/data/data.json');

App({
  onLaunch() {
    console.log("App::onLaunch() is called")
    wx.setNavigationBarTitle({
      title: this.globalData.data.name,
    });
    if (this.globalData.showFloors) {
      this.globalData.showFloors();
    }
  },
  globalData: {
    data: localData
  },
  getParkingLotInfo() {
    const n2 = Math.floor(Math.random() * 100);
    const n1 = Math.floor(Math.random() * n2);
    const info = `负一楼停车场剩余车位：${n1}，负二楼停车场剩余车位：${n2}`;
    return info;
  }
})
