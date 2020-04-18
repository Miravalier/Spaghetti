package dev.miramontes.spaghetti.ui.home

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.ServerConnection
import dev.miramontes.spaghetti.library.generateDebugSpaghettiAmount
import dev.miramontes.spaghetti.library.getIdToken
import kotlinx.android.synthetic.main.fragment_home.*
import org.json.JSONObject

class HomeFragment : Fragment() {
    private var idToken: String? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        val amountTextView = root.findViewById<TextView>(R.id.amount)

        if (idToken != null && activity != null) {
            val serverConnection = ServerConnection(activity!!, idToken!!)
            serverConnection.balance(
                Response.Listener {response ->
                    amountTextView.text = String.format("%.2f", response.getDouble("balance"))
                },
                Response.ErrorListener {
                    Log.e("Spaghetti","Failed to Authenticate with the server")
                    amountTextView.text = "Network Error"
                    activity?.finish()
                }
            )
        }

        return root
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)

        idToken = getIdToken(context)
        if (idToken == null) {
            activity?.finish()
        }
    }
}