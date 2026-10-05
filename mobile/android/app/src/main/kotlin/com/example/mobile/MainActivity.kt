package com.example.mobile

import android.content.pm.PackageManager
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        // Tells Dart whether a Maps key was built in, so the Map tab can fall
        // back to its list. Only a boolean crosses the channel, never the key.
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "tripmate/maps")
            .setMethodCallHandler { call, result ->
                if (call.method == "hasApiKey") {
                    @Suppress("DEPRECATION")
                    val info =
                        packageManager.getApplicationInfo(
                            packageName,
                            PackageManager.GET_META_DATA,
                        )
                    val key = info.metaData?.getString("com.google.android.geo.API_KEY")
                    result.success(!key.isNullOrBlank())
                } else {
                    result.notImplemented()
                }
            }
    }
}
