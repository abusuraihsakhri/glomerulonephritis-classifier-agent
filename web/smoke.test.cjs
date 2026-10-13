"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
const html=fs.readFileSync("web/index.html","utf8");
const script=html.match(/<script>([\s\S]*?)<\/script>/i);
assert.ok(script);
const els=new Map();
function element(id){if(!els.has(id))els.set(id,{value:"",checked:false,textContent:"",disabled:true,handlers:{},addEventListener(type,fn){this.handlers[type]=fn}});return els.get(id)}
const ctx={document:{getElementById:element},console};
vm.runInNewContext(script[1],ctx,{filename:"web/index.html"});
function check(extra={}){return ctx.classify({task_id:"T1",target_identifier:"SYN-1",primary_metric:1,secondary_metric:1,status_descriptor:"NOMINAL",is_critical_flag:false,...extra})}
assert.equal(check().total_alerts,0);
assert.equal(check({primary_metric:26}).total_alerts,1);
assert.equal(check({secondary_metric:13}).overall_urgency,"ELEVATED_RISK");
assert.equal(check({is_critical_flag:true}).overall_urgency,"CRITICAL_STAT_PANIC");
assert.equal(check({status_descriptor:"DISCORDANT_ANOMALY"}).total_alerts,1);
element("task_id").value="T1";element("target_identifier").value="SYN-1";
element("primary_metric").value="26";element("secondary_metric").value="2";
element("status_descriptor").value="NOMINAL";
element("audit-form").handlers.submit({preventDefault(){}});
assert.equal(element("tasks").textContent,"1");
assert.equal(JSON.parse(element("output").textContent).total_alerts,1);
element("primary_metric").value="";
element("audit-form").handlers.submit({preventDefault(){}});
assert.match(element("error").textContent,/finite numbers/);
assert.equal(element("tasks").textContent,"1");
console.log("Browser demonstration smoke tests passed.");
