function uiEffects(data){
    console.log(data);
}


function uiEffectsAfterWrite(data){
    console.log(data);
}

function PushConnection () {
    var channels = [];
    this.connect = function(channel, acks) {
        channels = channel;
        acks_str = [];
        if(acks){
            acks_str = JSON.stringify(acks);
        }
        $.ajax({
            url: "/push2/channel/connections/",
            type: "POST",
            data: "channels=" + JSON.stringify(channels) + "&acks=" + acks_str,
            dataType: "json",
            success: function(msg) {
                if(msg){
                    // Override this function to have your personal effect
                    // in your applications after receive from channel
                    uiEffects(msg);
                }
                Push.connect(channels, Push.setAck(msg));
            },
            error: function(err){
                //Push.connect(channels);
            },
        });
    };
    this.write = function(write_channels, text) {
        time_send = new Date();
        $.ajax({
            url: "/push2/channel/write/",
            type: "POST",
            data: 'write_channels=' + JSON.stringify(write_channels) + '&text=' + JSON.stringify(text) +
                    "&time_send=" + time_send.getTime(),
            dataType: "json",
            success: function(msg) {
                // Override this function to have your personal effect
                // in your applications after write on channel
                if(msg){
                    uiEffectsAfterWrite(msg);
                }
            },
            error: function(err){
                console.log(err);
            },
        });
    };

    this.setAck = function(msg) {
        acks = []
        $.each(msg['data'], function(key, value) {
            acks = acks.concat(value['id']);
        });
        return acks;
    };
}
Push = new PushConnection();
