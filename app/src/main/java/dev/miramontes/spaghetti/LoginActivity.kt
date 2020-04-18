package dev.miramontes.spaghetti

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.android.volley.Response
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.auth.api.signin.GoogleSignInStatusCodes
import com.google.android.gms.common.SignInButton
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.tasks.RuntimeExecutionException
import dev.miramontes.spaghetti.library.ServerConnection
import dev.miramontes.spaghetti.library.setIdToken
import java.lang.RuntimeException


class LoginActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val signInButton = findViewById<SignInButton>(R.id.sign_in_button)
        signInButton.setSize(SignInButton.SIZE_WIDE)

        // Activate sign in button
        val googleSignInOptions = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(resources.getString(R.string.google_client_id))
            .requestEmail()
            .build()

        val googleSignInClient = GoogleSignIn.getClient(this, googleSignInOptions)

        signInButton.setOnClickListener {
            val signInIntent = googleSignInClient.signInIntent
            startActivityForResult(signInIntent, resources.getInteger(R.integer.RC_GOOGLE_SIGN_IN))
        }

        // Use previously signed in account if possible
        val account: GoogleSignInAccount? = GoogleSignIn.getLastSignedInAccount(this)
        if (account != null) {
            val serverConnection = ServerConnection(this, account.idToken!!)
            serverConnection.status(Response.Listener { response ->
                Log.d("Spaghetti", response.toString())
                onLogin(account)
            },
            Response.ErrorListener {
                Log.e("Spaghetti", "Failed to authenticate with cached credentials.")
            })
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        // Handle google sign in result
        if (requestCode == resources.getInteger(R.integer.RC_GOOGLE_SIGN_IN)) {
            try {
                val account = GoogleSignIn.getSignedInAccountFromIntent(data).result
                if (account != null) {
                    val idToken = account.idToken

                    onLogin(account)
                }
                else {
                    onError()
                }
            }
            catch (e: RuntimeException) {
                Log.e("Spaghetti", "Failed to log in: " + e.message)
                Log.e("Spaghetti", GoogleSignInStatusCodes.getStatusCodeString(8))
                onError()
            }

        }
    }

    private fun onError() {
        Toast.makeText(this, R.string.login_failed, Toast.LENGTH_LONG).show()
    }

    private fun onLogin(account: GoogleSignInAccount) {
        val idToken = account.idToken
        if (idToken != null) {
            setIdToken(this, idToken)
            Log.d("Spaghetti", "ID Token Saved")
            startActivity(Intent(this, MainActivity::class.java))
        }
        else {
            onError()
        }
    }
}