// Keep the compiler version used by the supplied working physical-watch app.
const fs=require('fs'),path=require('path');
const watchConfig=path.resolve('src/config-watch.json');
if(!fs.existsSync(watchConfig))throw Error('src/config-watch.json is required to generate the watch manifest');
JSON.parse(fs.readFileSync(watchConfig,'utf8'));
const toolkit=process.env.WATCH_COMPAT_TOOLKIT||path.join(__dirname,'compat-toolkit/node_modules/aiot-toolkit');
if(!fs.existsSync(path.join(toolkit,'package.json')))throw Error('Install the compatible compiler: npm install --prefix tools/compat-toolkit --ignore-scripts');
if(JSON.parse(fs.readFileSync(path.join(toolkit,'package.json'),'utf8')).version!=='1.1.0')throw Error('Compatible compiler must be aiot-toolkit 1.1.0');
if(process.env.WATCH_BUILD_TRACE==='1'){
 const req=require('module').createRequire(path.join(path.resolve(toolkit),'package.json')),webpack=req('webpack'),configPath=require.resolve(path.join(path.resolve(toolkit),'gen-webpack-conf')),original=require(configPath);
 require.cache[configPath].exports=(...args)=>{const config=original(...args);let previous='';config.plugins.push(new webpack.ProgressPlugin((p,message)=>{const stage=Math.floor(p*100)+' '+message;if(stage!==previous){previous=stage;console.log('BUILD_STAGE',stage);}}));return config;};
}
const {compile}=require(path.join(toolkit,'lib/commands/compile'));
(async()=>{
 // Offline conversion metadata is never read by the app. Keep source for tools,
 // but omit it while compiler/inner signature enumerate deployed common files.
 const metadata=path.resolve('src/common/assets.txt'),offline=path.resolve('reports/build-only-assets-'+process.pid+'.txt');
 fs.mkdirSync(path.dirname(offline),{recursive:true});let moved=false,result;
 try{if(fs.existsSync(metadata)){fs.renameSync(metadata,offline);moved=true;}result=await compile('native',process.argv.includes('--development')?'dev':'prod',false,{signMode:'BUILD'});}
 finally{if(moved)fs.renameSync(offline,metadata);}
 if(result.compileError||result.stats.hasErrors())throw Error('Compatible compiler failed');
 const watchManifest=path.resolve('build/manifest-watch.json');
 if(!fs.existsSync(watchManifest)||JSON.parse(fs.readFileSync(watchManifest,'utf8')).package!=='com.codex.steins0.rw5')throw Error('Watch-specific manifest was not generated correctly');
 const manifest=JSON.parse(fs.readFileSync('src/manifest.json','utf8'));
 const name=manifest.package+'.debug.'+manifest.versionName+'.rpk',file=path.join('dist',name);
 if(!fs.existsSync(file))throw Error('Current-version package was not produced');
 // 0.2.0: native binary resources and most small text use STORE; retain only
 // enough text DEFLATE to stay below 25 MB. This does not prove a firmware fix.
 await require('./install-low-memory-v020.cjs')(file,toolkit);
 // Use the release wrapping that resolved the earlier Summer Pockets install issue.
 const packaging=await require('./repack-rpk.cjs').repackRpk(file,file,toolkit);
 console.log('R1_PACKAGING',JSON.stringify(packaging));
 const bytes=fs.statSync(file).size;if(bytes>25000000)throw Error('Package exceeds the 25,000,000-byte cap: '+bytes);
 console.log('BUILD_OUTPUT',name,bytes);
})().catch(e=>{console.error(e);process.exitCode=1;});
