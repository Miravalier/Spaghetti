package dev.miramontes.spaghetti.ui.home

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.android.volley.Response
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.ServerConnection
import dev.miramontes.spaghetti.library.getIdToken

class HomeFragment : Fragment() {
    private var idToken: String = "NO_TOKEN";

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        val amountTextView = root.findViewById<TextView>(R.id.amount)

        activity?.let{ activity ->
            getIdToken(activity)?.let { newToken ->
                idToken = newToken
            }
            val serverConnection = ServerConnection(activity, idToken)
            serverConnection.netWorth(
                Response.Listener {response ->
                    amountTextView.text = String.format("%.2f spaghetti", response.getDouble("balance"))
                },
                Response.ErrorListener {
                    Log.e("Spaghetti","Failed to Authenticate with the server")
                    activity.finish()
                }
            )
        }

        return root
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)

        getIdToken(context)?.let { newToken ->
            idToken = newToken
        }

        if (idToken == "NO_TOKEN") {
            activity?.finish()
        }
    }
}